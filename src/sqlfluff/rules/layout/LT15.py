"""Implementation of Rule LT15."""

from typing import List, Optional

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_LT15(BaseRule):
    """Too many consecutive blank lines.

    **Anti-pattern**

    In this example, the maximum number of empty lines inside a statement is set to 0.

    .. code-block:: sql

        SELECT 'a' AS col
        FROM tab


        WHERE x = 4
        ORDER BY y


        LIMIT 5
        ;

    **Best practice**

    .. code-block:: sql

        SELECT 'a' AS col
        FROM tab
        WHERE x = 4
        ORDER BY y
        LIMIT 5
        ;

    """

    name = "layout.newlines"
    groups = ("all", "layout")
    config_keywords = [
        "maximum_empty_lines_between_statements",
        "maximum_empty_lines_inside_statements",
        "maximum_empty_lines_between_batches",
    ]
    crawl_behaviour = SegmentSeekerCrawler(types={"newline"}, provide_raw_stack=True)
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """There should be a maximum number of empty lines."""
        self.maximum_empty_lines_between_statements: int
        self.maximum_empty_lines_inside_statements: int
        self.maximum_empty_lines_between_batches: int
        context_seg = context.segment

        # Determine the appropriate maximum based on context
        # Check if we're inside a statement first (highest priority)
        if any(seg.is_type("statement") for seg in context.parent_stack):
            # If directly inside a with_compound_statement (between CTEs or between
            # the last CTE and the main query), use between_statements limit to avoid
            # conflicts with LT08 which requires blank lines after CTEs.
            if (
                context.parent_stack
                and context.parent_stack[-1].is_type("with_compound_statement")
            ):
                maximum_empty_lines = self.maximum_empty_lines_between_statements
            else:
                maximum_empty_lines = self.maximum_empty_lines_inside_statements
        # Check if we're inside a batch but not in a statement
        elif any(seg.is_type("batch") for seg in context.parent_stack):
            # Inside a batch (between statements in a batch)
            maximum_empty_lines = self.maximum_empty_lines_between_statements
        # At file level - check dialect to determine if between batches or statements
        elif context.dialect.name == "tsql":
            # In T-SQL at file level, we're between batches
            maximum_empty_lines = self.maximum_empty_lines_between_batches
        else:
            # Default: between statements
            maximum_empty_lines = self.maximum_empty_lines_between_statements

        if len(context.raw_stack) < maximum_empty_lines:  # pragma: no cover
            return None

        for raw_seg in context.raw_stack[-maximum_empty_lines - 1 :]:
            if raw_seg.is_templated or not raw_seg.is_type("newline"):
                return None

        return [
            LintResult(
                anchor=context_seg,
                fixes=[LintFix.delete(context_seg)],
            )
        ]
