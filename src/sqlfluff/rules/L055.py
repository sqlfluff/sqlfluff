"""Implementation of Rule L055."""
from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_groups


@document_groups
class Rule_L055(BaseRule):
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

    groups = ("all",)
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
