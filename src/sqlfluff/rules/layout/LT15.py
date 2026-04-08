"""Implementation of Rule LT15."""

from typing import List, Optional

from sqlfluff.core.parser.segments.common import NewlineSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_LT15(BaseRule):
    """Too many or too few consecutive blank lines.

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

    When ``minimum_empty_lines_between_statements`` is set to 1, all statements
    must be separated by at least one blank line.

    **Anti-pattern**

    .. code-block:: sql

        SELECT 1;
        SELECT 2;

    **Best practice**

    .. code-block:: sql

        SELECT 1;

        SELECT 2;

    """

    name = "layout.newlines"
    groups = ("all", "layout")
    config_keywords = [
        "maximum_empty_lines_between_statements",
        "maximum_empty_lines_inside_statements",
        "maximum_empty_lines_between_batches",
        "minimum_empty_lines_between_statements",
    ]
    crawl_behaviour = SegmentSeekerCrawler(types={"newline"}, provide_raw_stack=True)
    is_fix_compatible = True

    def _is_between_statements(self, context: RuleContext) -> bool:
        """Check if the current newline is between statements (not inside one)."""
        # Inside a statement but in a with_compound_statement parent -> between
        if any(seg.is_type("statement") for seg in context.parent_stack):
            if context.parent_stack and context.parent_stack[-1].is_type(
                "with_compound_statement"
            ):
                return True
            return False
        # Inside a batch but not in a statement -> between statements
        if any(seg.is_type("batch") for seg in context.parent_stack):
            return True
        # At file level in non-T-SQL -> between statements
        if context.dialect.name != "tsql":
            return True
        # T-SQL at file level -> between batches (not between statements)
        return False

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """There should be a maximum number of empty lines.

        Also enforces minimum empty lines between statements when configured.
        """
        self.maximum_empty_lines_between_statements: int
        self.maximum_empty_lines_inside_statements: int
        self.maximum_empty_lines_between_batches: int
        self.minimum_empty_lines_between_statements: int
        context_seg = context.segment

        # Determine the appropriate maximum based on context
        # Check if we're inside a statement first (highest priority)
        if any(seg.is_type("statement") for seg in context.parent_stack):
            # If directly inside a with_compound_statement (between CTEs or between
            # the last CTE and the main query), use between_statements limit to avoid
            # conflicts with LT08 which requires blank lines after CTEs.
            if context.parent_stack and context.parent_stack[-1].is_type(
                "with_compound_statement"
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

        # --- Maximum enforcement (existing logic) ---
        if len(context.raw_stack) >= maximum_empty_lines + 1:
            all_newlines = True
            for raw_seg in context.raw_stack[-maximum_empty_lines - 1 :]:
                if raw_seg.is_templated or not raw_seg.is_type("newline"):
                    all_newlines = False
                    break
            if all_newlines:
                return [
                    LintResult(
                        anchor=context_seg,
                        fixes=[LintFix.delete(context_seg)],
                    )
                ]

        # --- Minimum enforcement (new logic) ---
        # Only applies between statements, not inside them.
        minimum_empty_lines = self.minimum_empty_lines_between_statements
        if minimum_empty_lines > 0 and self._is_between_statements(context):
            # Check if this is the first newline in a sequence (the previous
            # raw segment is not a newline). This ensures we only trigger the
            # minimum check once per gap, avoiding duplicate fixes.
            if context.raw_stack and not context.raw_stack[-1].is_type("newline"):
                # This is the first newline after non-newline content.
                # Count consecutive newlines starting from this one by
                # looking at sibling segments after the current one.
                consecutive_newlines = 1  # The current one
                has_following_statement = False
                for sibling in context.siblings_post:
                    if sibling.is_type("newline"):
                        consecutive_newlines += 1
                    elif sibling.is_type("statement", "statement_terminator", "batch"):
                        # Found a statement or related content after the
                        # newline gap - we're truly between statements.
                        has_following_statement = True
                        break
                    elif sibling.is_type("whitespace"):
                        # Skip whitespace (e.g. indentation)
                        continue
                    else:
                        # Any other segment type (meta, end_of_file, etc.)
                        # means we're not between statements.
                        break

                # Only enforce minimum if there IS a following statement.
                # Don't add blank lines at end of file or before non-statement
                # content.
                if not has_following_statement:
                    return None

                # Number of empty lines = consecutive_newlines - 1
                empty_lines = consecutive_newlines - 1
                if empty_lines < minimum_empty_lines:
                    # Need to add more newlines
                    needed = minimum_empty_lines - empty_lines
                    return [
                        LintResult(
                            anchor=context_seg,
                            fixes=[
                                LintFix.create_after(
                                    context_seg,
                                    [NewlineSegment()] * needed,
                                )
                            ],
                        )
                    ]

        return None
