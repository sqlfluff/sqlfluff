"""Implementation of Rule L008."""
from typing import List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow.sequence import ReflowSequence


class Rule_L008(BaseRule):
    """Commas should be followed by a single whitespace unless followed by a comment.

    **Anti-pattern**

    In this example, there is no space between the comma and ``'zoo'``.

    .. code-block:: sql

        SELECT
            *
        FROM foo
        WHERE a IN ('plop','zoo')

    **Best practice**

    Keep a single space after the comma. The ``•`` character represents a space.

    .. code-block:: sql
       :force:

        SELECT
            *
        FROM foo
        WHERE a IN ('plop',•'zoo')
    """

    name = "spacing.commas"
    aliases = ("LS04",)
    groups = ("all", "core", "layout", "spacing")
    crawl_behaviour = SegmentSeekerCrawler({"comma"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Commas should not have whitespace directly before them."""
        return (
            ReflowSequence.from_around_target(
                context.segment,
                context.parent_stack[0],
                config=context.config,
                sides="after",
            )
            .respace()
            .get_results()
        )
