"""Implementation of Rule AM08."""

from typing import Optional, Tuple

from sqlfluff.core.parser import BaseSegment, KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
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
    groups: Tuple[str, ...] = ("all", "ambiguous")
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
            kw.raw_upper in ("CROSS", "POSITIONAL", "USING")
            for kw in join_clause_keywords
        ):
            # If explicit CROSS JOIN is used, disregard lack of condition
            # If explicit POSITIONAL JOIN is used, disregard lack of condition
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
            where_clause_simplifable = self._is_where_clause_simplifable(
                maybe_where_clause
            )
            if where_clause_simplifable:
                # For now, return violation without fix.
                return LintResult(
                    maybe_where_clause,
                    description="WHERE clause used for join condition. "
                    "Use explicit ON instead.",
                )
            else:
                # In case of complex expression, try to avoid false positive
                return None

        join_keywords = [kw for kw in join_clause_keywords if kw.raw_upper == "JOIN"]
        if len(join_keywords) != 1:
            # This can happen in T-SQL CROSS APPLY / OUTER APPLY
            return None

        join_kw = join_keywords[0]

        # Please note that this is exclusive on both sides.
        # This means we get all segments *after* join keyword.
        valid_segments = join_clause.select_children(start_seg=join_kw, stop_seg=None)

        return LintResult(
            join_clause,
            fixes=[
                LintFix.replace(
                    anchor_segment=join_clause,
                    edit_segments=[
                        KeywordSegment("CROSS" if join_kw.raw == "JOIN" else "cross"),
                        WhitespaceSegment(),
                        KeywordSegment(join_kw.raw),
                        *valid_segments,
                    ],
                ),
            ],
        )

    @staticmethod
    def _cross_join_supported(context: RuleContext) -> bool:
        return (
            False
            or "CROSS" in context.dialect.sets("reserved_keywords")
            or "CROSS" in context.dialect.sets("unreserved_keywords")
        )

    @staticmethod
    def _get_select_stmt(stack: Tuple[BaseSegment, ...]) -> Optional[BaseSegment]:
        for seg in reversed(stack):
            if seg.is_type("select_statement"):
                return seg
            elif seg.is_type("update_statement", "delete_statement"):
                return None

        # According to grammar, this is not reachable.
        # Do not emit any error instead of crashing.
        return None  # pragma: no cover

    @staticmethod
    def _is_where_clause_simplifable(where_clause: BaseSegment) -> bool:
        assert where_clause.is_type("where_clause")
        expr = where_clause.get_child("expression")
        if not expr:  # pragma: no cover
            # According to grammar, we should always have an ExpressionSegment
            # See sqlfluff.dialects.dialect_ansi.WhereClauseSegment
            return False
        ops = expr.get_children("binary_operator")
        return all(op.raw_upper == "AND" for op in ops)
