"""Implementation of Rule AM08."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AM08(BaseRule):
    """Implicit cross join detected.

    **Anti-pattern**

    Cross joins are valid, but rare in the wild - and more often created by mistake
    than on purpose. This rule catches situations where a cross join has been specified,
    but not explicitly and so the risk of a mistaken cross join is highly likely.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        JOIN baz;

    **Best practice**

    Use CROSS JOIN.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        CROSS JOIN baz;
    """

    name = "ambiguous.join_condition"
    aliases = ()
    groups: tuple[str, ...] = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"join_clause"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Find joins without ON clause.

        Fix them into CROSS JOIN (if dialect allows it).
        """
        if not self._cross_join_supported(context):  # pragma: no cover
            # At the time of implementation, all dialects supports CROSS JOIN syntax.
            # Therefore, no cover is used on if statement.
            return None

        # We are only interested in JOIN clauses.
        join_clause = context.segment
        assert join_clause.is_type("join_clause")

        join_clause_keywords = [
            seg for seg in join_clause.segments if seg.type == "keyword"
        ]

        if any(
            kw.raw_upper in ("CROSS", "POSITIONAL", "USING", "NATURAL")
            for kw in join_clause_keywords
        ):
            # If explicit CROSS JOIN is used, disregard lack of condition
            # If explicit POSITIONAL JOIN is used, disregard lack of condition
            # If explicit NATURAL JOIN is used, disregard lack of condition
            # If explicit JOIN USING is used, disregard lack of condition
            return None

        this_join_condition = join_clause.get_child("join_on_condition")
        if this_join_condition:
            # Join condition is present, no error reported.
            return None

        select_stmt = self._get_select_stmt(context.parent_stack)
        if select_stmt is None:
            # Do not emit this warning for JOIN in UPDATE or DELETE
            return None

        maybe_where_clause = select_stmt.get_child("where_clause")
        if maybe_where_clause:
            # See CV12
            return None

        join_keywords = [kw for kw in join_clause_keywords if kw.raw_upper == "JOIN"]
        if len(join_keywords) != 1:
            # This can happen in T-SQL CROSS APPLY / OUTER APPLY
            return None

        # Skip if join is part of flattening logic
        maybe_from_expression_element = join_clause.get_child("from_expression_element")
        if maybe_from_expression_element:
            for (
                function_name_identifier
            ) in maybe_from_expression_element.recursive_crawl(
                "function_name_identifier"
            ):
                if function_name_identifier.raw_upper == "UNNEST":
                    return None

        return LintResult(join_clause)

    @staticmethod
    def _cross_join_supported(context: RuleContext) -> bool:
        return (
            False
            or "CROSS" in context.dialect.sets("reserved_keywords")
            or "CROSS" in context.dialect.sets("unreserved_keywords")
        )

    @staticmethod
    def _get_select_stmt(stack: tuple[BaseSegment, ...]) -> Optional[BaseSegment]:
        for seg in reversed(stack):
            if seg.is_type("select_statement"):
                return seg
            elif seg.is_type("update_statement", "delete_statement"):
                return None

        # According to grammar, this is not reachable.
        # Do not emit any error instead of crashing.
        return None  # pragma: no cover
