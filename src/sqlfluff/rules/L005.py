"""Implementation of Rule L005."""
from typing import List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow.sequence import ReflowSequence


class Rule_L005(BaseRule):
    """Commas should not have whitespace directly before them.

    Unless it's an indent. Trailing/leading commas are dealt with
    in a different rule.

    **Anti-pattern**

    The ``•`` character represents a space.
    There is an extra space in line two before the comma.

    .. code-block:: sql
       :force:

        SELECT
            a•,
            b
        FROM foo

    **Best practice**

    Remove the space before the comma.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM foo
    """

    name = "spacing.commas"
    aliases = ("LS02",)
    groups = ("all", "core", "layout", "spacing")
    crawl_behaviour = SegmentSeekerCrawler({"comma"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Commas should not have whitespace directly before them."""
        results = (
            ReflowSequence.from_around_target(
                context.segment,
                context.parent_stack[0],
                config=context.config,
                sides="before",
            )
            .respace()
            .get_results()
        )
        # Because whitespace management is currently spread across a couple
        # of rules, we filter just to results with deletes in them here.
        return [
            result
            for result in results
            if all(fix.edit_type == "delete" for fix in result.fixes)
        ]
