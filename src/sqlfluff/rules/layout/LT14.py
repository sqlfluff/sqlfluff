"""Implementation of Rule LT14."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.reflow.sequence import ReflowSequence


class Rule_LT14(BaseRule):
    """Keyword clauses should follow a standard for being before/after newlines.

    **Anti-pattern**

    In this example, the keyword are not at the beginning of or alone on the line.

    .. code-block:: sql

        SELECT 'a' AS col FROM tab WHERE x = 4 ORDER BY y LIMIT 5

    **Best practice**

    .. code-block:: sql

        SELECT 'a' AS col
        FROM tab
        WHERE x = 4
        ORDER BY y
        LIMIT 5

    .. code-block:: sql

        SELECT 'a' AS col
        FROM
            tab
        WHERE
            x = 4
        ORDER BY
            y
        LIMIT
            5

    """

    name = "layout.keyword_newline"
    groups = ("all", "layout")
    crawl_behaviour = RootOnlyCrawler()
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Keyword clauses should begin on a newline."""
        return (
            ReflowSequence.from_root(context.segment, config=context.config)
            .rebreak("keywords")
            .get_results()
        )
