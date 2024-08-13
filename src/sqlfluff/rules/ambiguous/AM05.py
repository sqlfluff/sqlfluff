"""Implementation of Rule AM05."""

from typing import Optional, Tuple

from sqlfluff.core.parser import KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AM05(BaseRule):
    """Join clauses should be fully qualified.

    By default this rule is configured to enforce fully qualified ``INNER JOIN``
    clauses, but not ``[LEFT/RIGHT/FULL] OUTER JOIN``. If you prefer a stricter
    lint then this is configurable.

    **Anti-pattern**

    A join is used without specifying the **kind** of join.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        JOIN baz;

    **Best practice**

    Use ``INNER JOIN`` rather than ``JOIN``.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        INNER JOIN baz;
    """

    name = "ambiguous.join"
    aliases = ("L051",)
    groups: Tuple[str, ...] = ("all", "ambiguous")
    config_keywords = ["fully_qualify_join_types"]
    crawl_behaviour = SegmentSeekerCrawler({"join_clause"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Fully qualify JOINs."""
        # Config type hints
        self.fully_qualify_join_types: str

        # We are only interested in JOIN clauses.
        assert context.segment.is_type("join_clause")

        join_clause_keywords = [
            segment for segment in context.segment.segments if segment.type == "keyword"
        ]

        # Identify LEFT/RIGHT/OUTER JOIN and if the next keyword is JOIN.
        if (
            self.fully_qualify_join_types in ["outer", "both"]
            and join_clause_keywords[0].raw_upper in ["RIGHT", "LEFT", "FULL"]
            and join_clause_keywords[1].raw_upper == "JOIN"
        ):
            # Define basic-level OUTER capitalization based on JOIN
            outer_kw = ("outer", "OUTER")[join_clause_keywords[1].raw == "JOIN"]
            # Insert OUTER after LEFT/RIGHT/FULL
            return LintResult(
                context.segment.segments[0],
                fixes=[
                    LintFix.create_after(
                        context.segment.segments[0],
                        [WhitespaceSegment(), KeywordSegment(outer_kw)],
                    )
                ],
            )

        # Identify lone JOIN by looking at first child segment.
        if (
            self.fully_qualify_join_types in ["inner", "both"]
            and join_clause_keywords[0].raw_upper == "JOIN"
        ):
            # Define basic-level INNER capitalization based on JOIN
            inner_kw = ("inner", "INNER")[join_clause_keywords[0].raw == "JOIN"]
            # Replace lone JOIN with INNER JOIN.
            return LintResult(
                context.segment.segments[0],
                fixes=[
                    LintFix.create_before(
                        context.segment.segments[0],
                        [KeywordSegment(inner_kw), WhitespaceSegment()],
                    )
                ],
            )

        return None
