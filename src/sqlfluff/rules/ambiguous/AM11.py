"""Implementation of Rule AM11."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

# Aggregate functions shared by the ANSI and major warehouse dialects. Kept
# in step with AM10 and duplicated because rule modules are self-contained.
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

# The clauses a window function may never appear in. WHERE, JOIN ... ON,
# GROUP BY and HAVING are all resolved before window functions are computed.
_WINDOW_FORBIDDEN_CLAUSE_TYPES = (
    "where_clause",
    "join_on_condition",
    "groupby_clause",
    "having_clause",
)

# Aggregates only need a separate timing check in the row-level predicates.
_AGGREGATE_FORBIDDEN_CLAUSE_TYPES = ("where_clause", "join_on_condition")


def _has_own_over_clause(function_segment: BaseSegment) -> bool:
    """Whether this function, rather than an argument, is windowed."""
    found = False

    def _walk(seg: BaseSegment) -> None:
        nonlocal found
        if found or seg.is_type("select_statement"):
            return
        if seg is not function_segment and seg.is_type("function"):
            return
        if seg.is_type("over_clause"):
            found = True
            return
        for child in seg.segments:
            _walk(child)

    _walk(function_segment)
    return found


def _is_bare_aggregate_call(function_segment: BaseSegment) -> bool:
    """Is this a non-windowed call to one of the aggregate functions?

    A windowed aggregate (``SUM(x) OVER (...)``) is a different case,
    already covered by the window-function check in this same rule.
    """
    name_id = next(function_segment.recursive_crawl("function_name_identifier"), None)
    name = name_id.raw.lower() if name_id else None
    if name not in _AGGREGATE_FUNCTION_NAMES:
        return False
    return not _has_own_over_clause(function_segment)


def _own_level_functions(segment: BaseSegment) -> list[BaseSegment]:
    """``function`` segments in ``segment``, not inside a nested subquery.

    A subquery is its own query level with its own ``WHERE``: the crawler
    already visits it separately, so a function inside it must not also be
    attributed to the outer level's clause.
    """
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


def _own_level_clauses(segment: BaseSegment, clause_type: str) -> list[BaseSegment]:
    """Find clauses at this SELECT level without descending into subqueries."""
    found: list[BaseSegment] = []

    def _walk(seg: BaseSegment) -> None:
        if seg.is_type("select_statement"):
            return
        if seg.is_type(clause_type):
            found.append(seg)
            return
        for child in seg.segments:
            _walk(child)

    for child in segment.segments:
        _walk(child)
    return found


def _window_in_aggregate_argument(
    function_segment: BaseSegment,
) -> Optional[BaseSegment]:
    """Return a window clause used as an argument of a plain aggregate."""
    contents = next(function_segment.recursive_crawl("function_contents"), None)
    if contents is None:
        return None
    for inner in _own_level_functions(contents):
        over_clause = next(inner.recursive_crawl("over_clause"), None)
        if over_clause is not None:
            return over_clause
    return None


class Rule_AM11(BaseRule):
    """A value is referenced before the clause that would compute it runs.

    Window functions are computed only once the ``FROM``, ``WHERE``,
    ``GROUP BY`` and ``HAVING`` clauses have already been resolved: they
    operate on the rows those clauses have already produced. Using one
    inside ``WHERE``, ``GROUP BY`` or ``HAVING`` is therefore not a style
    preference but a logical impossibility -- the value the window function
    would need to compute over does not exist yet at that stage. This holds
    for any window function, not just the aggregate ones, and is rejected
    consistently by SQL engines rather than varying between them.

    ``WHERE`` runs earlier still: it filters individual rows before any
    grouping happens at all, so a plain (non-windowed) aggregate function
    cannot appear there either -- there is no group yet for it to aggregate.
    ``HAVING`` permits normal aggregate calls because it operates on groups.
    This rule's aggregate check is deliberately limited to ``WHERE``; it does
    not add a separate diagnostic for aggregate calls in ``GROUP BY``.

    A window function is legal in the projection or in ``ORDER BY``, since
    both are evaluated after grouping and filtering are complete.

    **Anti-pattern**

    ``HAVING`` is evaluated before window functions exist; ``WHERE`` is
    evaluated before any aggregate has anything to aggregate.

    .. code-block:: sql

        SELECT a
        FROM foo
        GROUP BY a
        HAVING SUM(x) OVER (PARTITION BY a) > 1

    .. code-block:: sql

        SELECT a
        FROM foo
        WHERE COUNT(*) > 1

    **Best practice**

    Move the condition to a plain aggregate in ``HAVING``, or filter using
    the value in a later step (for example, a subquery or CTE that computes
    it first).

    .. code-block:: sql

        SELECT a
        FROM foo
        GROUP BY a
        HAVING SUM(x) > 1 AND COUNT(*) > 1
    """

    name = "ambiguous.window_function_placement"
    groups: tuple[str, ...] = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """A value is referenced before the clause that computes it runs."""
        if not context.segment.is_type("select_statement"):
            return None

        for select_clause in _own_level_clauses(context.segment, "select_clause"):
            for fn in _own_level_functions(select_clause):
                if _is_bare_aggregate_call(fn):
                    over_clause = _window_in_aggregate_argument(fn)
                    if over_clause is not None:
                        return LintResult(anchor=over_clause)

        for clause_type in _WINDOW_FORBIDDEN_CLAUSE_TYPES:
            for clause in _own_level_clauses(context.segment, clause_type):
                for fn in _own_level_functions(clause):
                    if any(fn.recursive_crawl("over_clause")):
                        over_clause = next(fn.recursive_crawl("over_clause"))
                        return LintResult(anchor=over_clause)

        for clause_type in _AGGREGATE_FORBIDDEN_CLAUSE_TYPES:
            for clause in _own_level_clauses(context.segment, clause_type):
                for fn in _own_level_functions(clause):
                    if _is_bare_aggregate_call(fn):
                        return LintResult(anchor=fn)

        return None
