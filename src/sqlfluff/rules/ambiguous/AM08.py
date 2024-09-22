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

    A join is used without specifying join condition.
    This can cause unintended cross join behavior.
    Prefer explicit const condition instead.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        JOIN baz;

    **Best practice**

    Use const condition instead.

    .. code-block:: sql
       :force:

        SELECT
            foo
        FROM bar
        JOIN baz
        ON 1=1;

    If dialect allows, alternatively use CROSS JOIN.

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
        """Always apply join condition."""
        # We are only interested in JOIN clauses.
        join_clause = context.segment
        assert join_clause.is_type("join_clause")

        join_clause_keywords = [
            segment for segment in join_clause.segments if segment.type == "keyword"
        ]
        if join_clause_keywords[0].raw_upper in "CROSS":
            # If explicit cross join is used, disregard lack of condition
            return None

        this_join_conditions = join_clause.get_children("join_on_condition")
        if not this_join_conditions:
            on_kw = "ON" if join_clause_keywords[-1].raw == "JOIN" else "on"
            return LintResult(
                join_clause,
                fixes=[
                    LintFix.create_after(
                        anchor_segment=join_clause.segments[-1],
                        edit_segments=[
                            WhitespaceSegment(),
                            KeywordSegment(on_kw),
                            WhitespaceSegment(),
                            LiteralSegment("1", type="numeric_literal"),
                            ComparisonOperatorSegment("="),
                            LiteralSegment("1", type="numeric_literal"),
                        ],
                    ),
                ],
            )

        return None
