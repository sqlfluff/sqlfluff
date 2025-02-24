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
    ]
    crawl_behaviour = SegmentSeekerCrawler(types={"newline"}, provide_raw_stack=True)
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """There should be a maximum number of empty lines."""
        self.maximum_empty_lines_between_statements: int
        self.maximum_empty_lines_inside_statements: int
        context_seg = context.segment

        maximum_empty_lines = (
            self.maximum_empty_lines_inside_statements
            if any(seg.is_type("statement") for seg in context.parent_stack)
            else self.maximum_empty_lines_between_statements
        )

        if len(context.raw_stack) < maximum_empty_lines:
            return None

        if all(
            raw_seg.is_type("newline")
            for raw_seg in context.raw_stack[-maximum_empty_lines - 1 :]
        ):

            return [
                LintResult(
                    anchor=context_seg,
                    fixes=[LintFix.delete(context_seg)],
                )
            ]

        return None
