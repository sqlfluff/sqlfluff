"""Implementation of Rule OR01."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_OR01(BaseRule):
    """Remove empty batches.

    **Anti-pattern**

    Empty batches (containing only / statements) should be removed.

    .. code-block:: sql
       :force:

        SELECT 1 FROM DUAL;

        /

        /

    **Best practice**

    Remove empty batches.

    .. code-block:: sql
       :force:

        SELECT 1 FROM DUAL;

        /
    """

    name = "oracle.empty_batch"
    aliases = ()
    groups = ("all", "oracle")
    crawl_behaviour = SegmentSeekerCrawler({"batch"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Remove empty batches."""
        # Rule only applies to Oracle syntax.
        if context.dialect.name != "oracle":
            return None  # pragma: no cover

        if not context.segment.is_type("batch"):  # pragma: no cover
            return None

        # Get all non-whitespace, non-meta segments
        content_segments = [
            s
            for s in context.segment.segments
            if not s.is_type("whitespace", "newline", "indent", "dedent")
            and not s.is_meta
        ]

        # Check if batch contains only slash_buffer_executor statement
        has_real_content = False
        has_slash = False
        for content_seg in content_segments:
            if content_seg.is_type("slash_buffer_executor"):
                has_slash = True
            elif not content_seg.is_meta:
                has_real_content = True
                break

        # If batch has no real content (only / and whitespace), remove it
        if not has_real_content and has_slash:
            fixes = [LintFix.delete(context.segment)]

            # Also delete the trailing newline after the batch if present
            segments = context.parent_stack[-1].segments
            idx = segments.index(context.segment)
            if idx + 1 < len(segments):
                next_seg = segments[idx + 1]
                if next_seg.is_type("newline"):
                    fixes.append(LintFix.delete(next_seg))

            return [
                LintResult(
                    anchor=context.segment,
                    description="Empty batch with only / statement should be removed.",
                    fixes=fixes,
                )
            ]

        return None
