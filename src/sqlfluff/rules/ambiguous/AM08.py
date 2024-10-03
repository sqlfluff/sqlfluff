"""Implementation of Rule AM08."""

from typing import Optional, Tuple

from sqlfluff.core.parser import (
    ComparisonOperatorSegment,
    KeywordSegment,
    LiteralSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AM08(BaseRule):
    """Join clauses should be present.

    **Anti-pattern**

    Cross joins are valid, but rare in the wild - and more often created by mistake than on purpose.
    This rule catches situations where a cross join has been specified,
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
        """Find joins without ON clause, fix them into CROSS JOIN (if dialect allows it)."""

        cross_join_supported = (
            False
            or "CROSS" in context.dialect.sets("reserved_keywords")
            or "CROSS" in context.dialect.sets("unreserved_keywords")
        )
        if not cross_join_supported:  # pragma: no cover
            # At the time of implementation, there was no dialect which didn't support CROSS JOIN syntax.
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

        join_keywords = [kw for kw in join_clause_keywords if kw.raw_upper == "JOIN"]
        assert len(join_keywords) == 1

        join_kw = join_keywords[0]

        # Please note that this is exclusive on both sides, meaning we get all segments *after* join keyword
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
