"""Implementation of Rule TQ03."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_TQ03(BaseRule):
    """Remove empty batches.

    **Anti-pattern**

    Empty batches (containing only GO statements) should be removed.

    .. code-block:: sql
       :force:

        CREATE TABLE dbo.test (
            testcol1 INT NOT NULL,
            testcol2 INT NOT NULL
        );

        GO

        GO

    **Best practice**

    Remove empty batches.

    .. code-block:: sql
       :force:

        CREATE TABLE dbo.test (
            testcol1 INT NOT NULL,
            testcol2 INT NOT NULL
        );

        GO
    """

    name = "tsql.empty_batch"
    aliases = ()
    groups = ("all", "tsql")
    crawl_behaviour = SegmentSeekerCrawler({"batch"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Remove empty batches."""
        # Rule only applies to T-SQL syntax.
        if context.dialect.name != "tsql":
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

        # Check if batch contains only GO statement
        has_real_content = False
        has_go = False
        for content_seg in content_segments:
            if content_seg.is_type("go_statement"):
                has_go = True
            elif not content_seg.is_meta:
                has_real_content = True
                break

        # If batch has no real content (only GO and whitespace), remove it
        if not has_real_content and has_go:
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
                    description="Empty batch with only GO statement should be removed.",
                    fixes=fixes,
                )
            ]

        return None
