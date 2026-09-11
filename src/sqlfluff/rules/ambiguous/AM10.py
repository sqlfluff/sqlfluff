"""Implementation of Rule AM10."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp

# Aggregate functions shared by the ANSI and major warehouse dialects.
_AGGREGATE_FUNCTION_NAMES = frozenset(
    {
        "count",
        "sum",
        "avg",
        "min",
        "max",
        "array_agg",
        "string_agg",
        "stddev",
        "stddev_pop",
        "stddev_samp",
        "variance",
        "var_pop",
        "var_samp",
        "bool_and",
        "bool_or",
        "every",
        "bit_and",
        "bit_or",
        "json_agg",
        "json_arrayagg",
        "json_objectagg",
        "listagg",
        "group_concat",
    }
)


def _function_name(function_segment: BaseSegment) -> Optional[str]:
    """The lowercased name of a ``function`` segment, if it has one."""
    name_id = next(function_segment.recursive_crawl("function_name_identifier"), None)
    return name_id.raw.lower() if name_id else None


def _is_aggregate_call(function_segment: BaseSegment) -> bool:
    """Is this a non-windowed call to one of the aggregate functions?

    A windowed aggregate (``SUM(x) OVER (...)``) does not collapse rows the
    way a grouped aggregate does, so it is not subject to the projection
    restrictions this rule checks.
    """
    if _function_name(function_segment) not in _AGGREGATE_FUNCTION_NAMES:
        return False
    return not any(function_segment.recursive_crawl("over_clause"))


def _has_nested_aggregate(function_segment: BaseSegment) -> bool:
    """Does an aggregate call have another aggregate call among its args?"""
    contents = next(function_segment.recursive_crawl("function_contents"), None)
    if contents is None:
        return False
    return any(
        _is_aggregate_call(inner)
        for inner in _own_level_functions(contents)
        if inner is not function_segment
    )


def _own_level_functions(segment: BaseSegment) -> list[BaseSegment]:
    """Find functions without crossing into a nested SELECT scope."""
    found: list[BaseSegment] = []

    def _walk(seg: BaseSegment) -> None:
        if seg.is_type("select_statement"):
            return
        if seg.is_type("function"):
            found.append(seg)
        for child in seg.segments:
            _walk(child)

    for child in segment.segments:
        _walk(child)
    return found


def _bare_column_refs(
    segment: BaseSegment, group_expressions: set[str]
) -> list[BaseSegment]:
    """Column references in ``segment``, outside of any aggregate call.

    Columns used only as *inputs* to an aggregate (``COUNT(a)``) are not
    collected -- an aggregate consumes whatever it is given. Only column
    references that survive outside of aggregate calls are potentially
    subject to the "must be a grouping key" restriction.
    """
    found: list[BaseSegment] = []

    def _walk(seg: BaseSegment) -> None:
        if seg.is_type("select_statement"):
            return
        if seg.is_type("expression", "bracketed", "function") and (
            _normalized_expression(seg) in group_expressions
        ):
            # A complete grouping expression can be projected as a value of
            # the group. Its component references are not bare columns.
            return
        if seg.is_type("column_reference"):
            found.append(seg)
            return
        if seg.is_type("function") and (
            _is_aggregate_call(seg) or any(seg.recursive_crawl("over_clause"))
        ):
            # Do not descend into an aggregate's own arguments: those
            # columns are consumed by the aggregate, not projected bare.
            # A windowed call (has an OVER clause) does not collapse rows
            # at all, so its contents are exempt from this restriction
            # entirely, not just the columns fed to the aggregate itself.
            return
        for child in seg.segments:
            _walk(child)

    for child in segment.segments:
        _walk(child)
    return found


def _group_by_keys(groupby_clause: BaseSegment) -> set[str]:
    """The lowercased names of the plain-variable GROUP BY keys.

    Only a ``column_reference`` that is a *direct* child of the clause
    counts: grouping by a computed expression (``GROUP BY (a + b)``) does
    not make the variables inside that expression individually available,
    it makes the expression's *result* the group key.
    """
    return {
        _normalized_expression(child)
        for child in groupby_clause.segments
        if child.is_type("column_reference")
    }


def _normalized_expression(segment: BaseSegment) -> str:
    """Return a comparable ANSI expression spelling.

    Unquoted identifiers and keywords are case-insensitive, while quoted
    identifiers and string literals retain their case. Redundant parentheses
    around an entire expression do not change the grouping key it denotes.
    """
    raw = segment.raw
    normalized: list[str] = []
    quote: Optional[str] = None
    index = 0

    while index < len(raw):
        char = raw[index]
        if quote:
            normalized.append(char)
            if char == quote:
                if index + 1 < len(raw) and raw[index + 1] == quote:
                    normalized.append(raw[index + 1])
                    index += 1
                else:
                    quote = None
        elif char in ("'", '"'):
            quote = char
            normalized.append(char)
        elif not char.isspace():
            normalized.append(char.lower())
        index += 1

    return _strip_outer_parentheses("".join(normalized))


def _strip_outer_parentheses(expression: str) -> str:
    """Remove parentheses only when they enclose the whole expression."""
    while expression.startswith("(") and expression.endswith(")"):
        depth = 0
        quote: Optional[str] = None
        closes_at_end = True
        index = 0

        while index < len(expression):
            char = expression[index]
            if quote:
                if char == quote:
                    if index + 1 < len(expression) and expression[index + 1] == quote:
                        index += 1
                    else:
                        quote = None
            elif char in ("'", '"'):
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and index != len(expression) - 1:
                    closes_at_end = False
                    break
            index += 1

        if depth or not closes_at_end:
            break
        expression = expression[1:-1]
    return expression


def _group_by_expressions(groupby_clause: BaseSegment) -> set[str]:
    """Return the complete expressions used as GROUP BY keys.

    A computed grouping key is available as that same expression, but its
    component columns are not independently available. Keeping complete
    expression spellings separate from :func:`_group_by_keys` preserves that
    distinction.
    """
    return {
        _normalized_expression(child)
        for child in groupby_clause.segments
        if child.is_type("expression", "bracketed", "column_reference", "function")
    }


class Rule_AM10(BaseRule):
    """Aggregate projection restrictions are not enforced.

    In a query that uses aggregation -- either explicitly via ``GROUP BY``,
    or implicitly by using an aggregate function with no ``GROUP BY`` at
    all -- anything projected or referenced in ``HAVING`` outside of an
    aggregate call must be one of the ``GROUP BY`` keys. A bare column that
    is neither a grouping key nor wrapped in an aggregate is ambiguous: it
    has no well-defined single value per group. The same restriction
    applies to ``HAVING``, since it is evaluated per group, after the
    grouping has already happened.

    Aggregate functions may not be nested inside one another either
    (``SUM(COUNT(x))``): each aggregate already collapses its group, so
    there is nothing left for an outer aggregate to further collapse.

    A windowed aggregate (using ``OVER``) does not collapse rows, so it is
    exempt from this restriction.

    **Anti-pattern**

    ``b`` is projected bare, but the query only groups by ``a``.

    .. code-block:: sql

        SELECT a, b, COUNT(*)
        FROM foo
        GROUP BY a

    **Best practice**

    Add the column to ``GROUP BY``, or wrap it in an aggregate.

    .. code-block:: sql

        SELECT a, b, COUNT(*)
        FROM foo
        GROUP BY a, b
    """

    name = "ambiguous.aggregate_projection"
    groups: tuple[str, ...] = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Aggregate projection restrictions are not enforced."""
        if not context.segment.is_type("select_statement"):
            return None
        segment = FunctionalContext(context).segment

        groupby_clause = next(
            iter(segment.children(sp.is_type("groupby_clause"))), None
        )
        select_clause = next(iter(segment.children(sp.is_type("select_clause"))), None)
        having_clause = next(iter(segment.children(sp.is_type("having_clause"))), None)
        if select_clause is None:
            return None

        select_targets = [
            child
            for child in select_clause.segments
            if child.is_type("select_clause_element")
        ]
        select_functions = [
            fn for el in select_targets for fn in _own_level_functions(el)
        ]
        having_functions = (
            _own_level_functions(having_clause) if having_clause is not None else []
        )
        aggregate_calls = [
            fn for fn in select_functions + having_functions if _is_aggregate_call(fn)
        ]

        # Nested aggregates are invalid regardless of GROUP BY.
        for fn in aggregate_calls:
            if _has_nested_aggregate(fn):
                return LintResult(anchor=fn)

        has_aggregation = bool(groupby_clause) or bool(aggregate_calls)
        if not has_aggregation:
            return None

        group_keys = _group_by_keys(groupby_clause) if groupby_clause else set()
        group_expressions = (
            _group_by_expressions(groupby_clause) if groupby_clause else set()
        )

        for target in select_targets:
            for ref in _bare_column_refs(target, group_expressions):
                if _normalized_expression(ref) not in group_keys:
                    return LintResult(anchor=ref)

        if having_clause is not None:
            for ref in _bare_column_refs(having_clause, group_expressions):
                if _normalized_expression(ref) not in group_keys:
                    return LintResult(anchor=ref)

        return None
