"""Implementation of Rule L065."""
from typing import List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.reflow.sequence import ReflowSequence


class Rule_L065(BaseRule):
    """Set operators should be surrounded by newlines.

    **Anti-pattern**

    In this example, `UNION ALL` is not on a line itself.

    .. code-block:: sql

        SELECT 'a' AS col UNION ALL
        SELECT 'b' AS col

    **Best practice**

    .. code-block:: sql

        SELECT 'a' AS col
        UNION ALL
        SELECT 'b' AS col

    """

    groups = ("all",)
    is_fix_compatible = True
    crawl_behaviour = SegmentSeekerCrawler({"set_operator"})

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Set operators should be surrounded by newlines.

        For any set operator we check if there is any NewLineSegment in the non-code
        segments preceding or following it.

        In particular, as part of this rule we allow multiple NewLineSegments.
        """
        return (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_results()
        )
