from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext, LintFix
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.parser import NewlineSegment

class Rule_OR01(BaseRule):
    """Slash terminator should be on a new line.

    **Anti-pattern**

    .. code-block:: sql

        SELECT 1 FROM dual; /

    **Best practice**

    .. code-block:: sql

        SELECT 1 FROM dual;
        /
    """

    name = "oracle.slash_terminator"
    aliases = ("L069",)  # Using a new code
    groups = ("all", "oracle")
    crawl_behaviour = SegmentSeekerCrawler({"statement_terminator"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Slash terminator should be on a new line."""

        if context.dialect.name != "oracle":
            return None

        if context.segment.raw.strip() != "/":
            return None

        if context.segment.pos_marker.source_slice.start == 0:
            return None

        if not context.parent_stack:
            return None

        siblings = context.parent_stack[-1].segments
        try:
            idx = siblings.index(context.segment)
        except ValueError:
            return None

        if idx > 0:
            prev_seg = siblings[idx - 1]
            if not (prev_seg.is_type("newline") or (prev_seg.is_type("whitespace") and "\n" in prev_seg.raw)):
                return LintResult(
                    anchor=context.segment,
                    description="Slash terminator should be on a new line.",
                    fixes=[
                        LintFix.create_before(
                            context.segment,
                            [NewlineSegment()],
                        )
                    ]
                )

        return None
