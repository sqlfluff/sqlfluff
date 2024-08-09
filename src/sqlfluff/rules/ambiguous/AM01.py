"""Implementation of Rule AM01."""

from typing import Optional, Tuple

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp


class Rule_AM01(BaseRule):
    """Ambiguous use of ``DISTINCT`` in a ``SELECT`` statement with ``GROUP BY``.

    When using ``GROUP BY`` a `DISTINCT`` clause should not be necessary as every
    non-distinct ``SELECT`` clause must be included in the ``GROUP BY`` clause.

    **Anti-pattern**

    ``DISTINCT`` and ``GROUP BY`` are conflicting.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
        GROUP BY a

    **Best practice**

    Remove ``DISTINCT`` or ``GROUP BY``. In our case, removing ``GROUP BY`` is better.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
    """

    name = "ambiguous.distinct"
    aliases = ("L021",)
    groups: Tuple[str, ...] = ("all", "core", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Ambiguous use of DISTINCT in select statement with GROUP BY."""
        segment = FunctionalContext(context).segment
        # We know it's a select_statement from the seeker crawler
        assert segment.all(sp.is_type("select_statement"))
        # Do we have a group by clause
        if segment.children(sp.is_type("groupby_clause")):
            # Do we have the "DISTINCT" keyword in the select clause
            distinct = (
                segment.children(sp.is_type("select_clause"))
                .children(sp.is_type("select_clause_modifier"))
                .children(sp.is_type("keyword"))
                .select(sp.is_keyword("distinct"))
            )
            if distinct:
                return LintResult(anchor=distinct[0])
        return None
