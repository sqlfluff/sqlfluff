"""Implementation of Rule L001."""
from typing import List
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.reflow import ReflowSequence


class Rule_L001(BaseRule):
    """Unnecessary trailing whitespace.

    **Anti-pattern**

    The ``•`` character represents a space.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo••

    **Best practice**

    Remove trailing spaces.

    .. code-block:: sql

        SELECT
            a
        FROM foo
    """

    name = "trailing-whitespace"
    aliases = ("LS01",)
    groups = ("all", "core", "layout", "spacing")
    crawl_behaviour = RootOnlyCrawler()
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Unnecessary trailing whitespace.

        Look for newline segments, and then evaluate what
        it was preceded by.
        """
        sequence = ReflowSequence.from_root(context.segment, config=context.config)
        return sequence.respace(filter="newline").get_results()
