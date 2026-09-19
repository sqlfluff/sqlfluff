"""Implementation of Rule AM12."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


def _normalized_identifier(raw: str) -> str:
    """Return a comparable spelling for a CTE name or a reference to one.

    Unquoted identifiers are case-insensitive, so they are lower-cased.
    Quoted identifiers keep their case, so only the surrounding quote
    characters are removed.
    """
    stripped = raw.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in ("'", '"'):
        return stripped[1:-1]
    return stripped.lower()


def _cte_name(cte_definition: BaseSegment) -> Optional[str]:
    """The declared name of a ``common_table_expression`` segment."""
    for child in cte_definition.segments:
        if child.is_type("identifier"):
            return _normalized_identifier(child.raw)
    return None


def _unqualified_reference_name(table_reference: BaseSegment) -> Optional[str]:
    """The bare name of a ``table_reference``, or ``None`` if it is qualified.

    A CTE name is never schema- or table-qualified, so ``public.cte1`` can
    never be a reference to a CTE named ``cte1`` and must not be treated as
    one.
    """
    identifiers = [
        child for child in table_reference.segments if child.is_type("identifier")
    ]
    if len(identifiers) != 1:
        return None
    return _normalized_identifier(identifiers[0].raw)


def _own_scope_table_references(segment: BaseSegment) -> list[BaseSegment]:
    """``table_reference`` segments that belong to this WITH block's scope.

    A nested ``WITH`` clause introduces its own CTE names, which shadow
    this block's names for everything inside it, so the walk stops there
    rather than attributing its references to this outer scope. An
    ordinary subquery is different: it does not start a new CTE scope, so
    a reference to a later sibling buried inside a subquery in a CTE's own
    body is exactly as illegal as one written directly in that body, and
    the walk must continue into it rather than stop.
    """
    found: list[BaseSegment] = []

    def _walk(seg: BaseSegment) -> None:
        if seg.is_type("with_compound_statement"):
            return
        if seg.is_type("table_reference"):
            found.append(seg)
            return
        for child in seg.segments:
            _walk(child)

    for child in segment.segments:
        _walk(child)
    return found


class Rule_AM12(BaseRule):
    """A CTE is referenced before its definition is complete.

    Within one ``WITH`` block, each common table expression may only
    reference common table expressions that were already fully defined
    earlier in the same block -- referencing a sibling defined later, or
    referencing itself, means the engine would need the result of a query
    it has not finished building yet, which is not possible. ``WITH
    RECURSIVE`` relaxes this in exactly one way: a common table expression
    may reference itself, because the engine builds it up one iteration at
    a time rather than needing the whole result at once. It does not allow
    a common table expression to reference a different sibling defined
    later, and it does not allow two common table expressions to reference
    each other, since neither of those forms can be built up iteratively
    the way a single self-reference can. The final query that follows the
    ``WITH`` block may always reference any of the block's common table
    expressions, since it runs only once every one of them is complete.

    A common table expression's own name is visible to every reference
    inside its body, including one buried inside a subquery, since a plain
    subquery does not start a new naming scope. A nested ``WITH`` block
    is different: the common table expressions it defines are a separate
    scope, and a name it reuses from an enclosing block refers to its own,
    inner definition rather than the outer one.

    **Anti-pattern**

    ``later`` is defined after ``first``, so ``first`` cannot reference it.

    .. code-block:: sql

        WITH first AS (SELECT * FROM later), later AS (SELECT 1 AS x)
        SELECT * FROM first

    A common table expression referencing itself without ``RECURSIVE``:

    .. code-block:: sql

        WITH cte AS (SELECT * FROM cte)
        SELECT * FROM cte

    **Best practice**

    Reorder the common table expressions so each one only reaches back to
    ones already defined, or add ``RECURSIVE`` for a genuine self-reference.

    .. code-block:: sql

        WITH later AS (SELECT 1 AS x), first AS (SELECT * FROM later)
        SELECT * FROM first
    """

    name = "ambiguous.cte_reference_order"
    groups: tuple[str, ...] = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"with_compound_statement"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """A CTE is referenced before its definition is complete."""
        segment = context.segment
        if not segment.is_type("with_compound_statement"):
            return None

        is_recursive = any(
            child.is_type("keyword") and child.raw.upper() == "RECURSIVE"
            for child in segment.segments
        )

        cte_definitions = [
            child
            for child in segment.segments
            if child.is_type("common_table_expression")
        ]
        if not cte_definitions:
            return None

        positions: dict[str, int] = {}
        for index, cte in enumerate(cte_definitions):
            name = _cte_name(cte)
            if name is not None and name not in positions:
                positions[name] = index

        for index, cte in enumerate(cte_definitions):
            for ref in _own_scope_table_references(cte):
                ref_name = _unqualified_reference_name(ref)
                if ref_name is None:
                    continue
                target_index = positions.get(ref_name)
                if target_index is None:
                    continue
                if target_index > index:
                    return LintResult(anchor=ref)
                if target_index == index and not is_recursive:
                    return LintResult(anchor=ref)

        return None
