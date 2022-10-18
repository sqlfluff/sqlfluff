"""Implementation of Rule L065."""
from typing import List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
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

    crawl_behaviour = SegmentSeekerCrawler({"set_operator"})

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Set operators should be surrounded by newlines.

        For any set operator we check if there is any NewLineSegment in the non-code
        segments preceding or following it.

        In particular, as part of this rule we allow multiple NewLineSegments.
        """
        pre_fixes, _, post_fixes = (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_partitioned_fixes(context.segment)
        )

        results = []
        if pre_fixes:
            results.append(
                LintResult(
                    anchor=context.segment,
                    description=(
                        "Set operators should be surrounded by newlines. "
                        f"Missing newline before set operator {context.segment.raw}."
                    ),
                    fixes=pre_fixes,
                )
            )
        if post_fixes:
            results.append(
                LintResult(
                    anchor=context.segment,
                    description=(
                        "Set operators should be surrounded by newlines. "
                        f"Missing newline after set operator {context.segment.raw}."
                    ),
                    fixes=post_fixes,
                )
            )

        return results
