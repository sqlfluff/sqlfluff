"""Implementation of Rule CV08."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV08(BaseRule):
    """Use ``LEFT JOIN`` instead of ``RIGHT JOIN``.

    **Anti-pattern**

    ``RIGHT JOIN`` is used.

    .. code-block:: sql
       :force:

        SELECT
            foo.col1,
            bar.col2
        FROM foo
        RIGHT JOIN bar
            ON foo.bar_id = bar.id;

    **Best practice**

    Refactor and use ``LEFT JOIN`` instead.

    .. code-block:: sql
       :force:

        SELECT
            foo.col1,
            bar.col2
        FROM bar
        LEFT JOIN foo
            ON foo.bar_id = bar.id;
    """

    name = "convention.left_join"
    aliases = ("L055",)
    groups = ("all", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"join_clause"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Use LEFT JOIN instead of RIGHT JOIN."""
        # We are only interested in JOIN clauses.
        assert context.segment.is_type("join_clause")

        # Identify if RIGHT JOIN is present.
        if {"RIGHT", "JOIN"}.issubset(
            {segment.raw_upper for segment in context.segment.segments}
        ):
            return LintResult(context.segment.segments[0])

        return None
