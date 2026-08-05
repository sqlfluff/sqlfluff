"""Implementation of Rule LT15."""

from typing import List, Optional

from sqlfluff.core.parser import NewlineSegment
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

    A minimum can also be required between statements. With
    ``minimum_empty_lines_between_statements = 1``, this is an anti-pattern:

    .. code-block:: sql

        SELECT a FROM tab;
        SELECT b FROM tab;

    and this is the best practice:

    .. code-block:: sql

        SELECT a FROM tab;

        SELECT b FROM tab;

    The minimum defaults to ``0``, which leaves the rule's existing behaviour
    unchanged.
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

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """There should be a maximum number of empty lines."""
        self.maximum_empty_lines_between_statements: int
        self.maximum_empty_lines_inside_statements: int
        self.maximum_empty_lines_between_batches: int
        self.minimum_empty_lines_between_statements: int
        context_seg = context.segment

        # A minimum only makes sense between statements, so it is checked where we
        # are not inside one. It runs first because the two cannot both fire on the
        # same gap: one wants newlines added, the other wants them removed.
        if not any(seg.is_type("statement") for seg in context.parent_stack):
            minimum_result = self._check_minimum(context)
            if minimum_result:
                return minimum_result

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

    def _check_minimum(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Require at least ``minimum_empty_lines_between_statements`` blank lines.

        Fires on the last newline of a run so the whole gap is measured once, rather
        than once per newline in it.
        """
        minimum = self.minimum_empty_lines_between_statements
        if not minimum:
            return None

        # Only act on the last newline of the run; otherwise the same gap would be
        # reported several times over. Whitespace is skipped both here and in the
        # backward walk below, so a line of spaces still counts as blank.
        following = [
            seg
            for seg in context.siblings_post
            if not seg.is_type("dedent", "indent", "whitespace")
        ]
        if following and following[0].is_type("newline"):
            return None

        # Skip when nothing but the end of the file follows, so there is no gap to
        # pad, and when the newline is templated, since that is not ours to rewrite.
        if context.segment.is_templated or not any(
            seg.is_code for seg in context.siblings_post
        ):
            return None

        # Count the run of newlines ending at this one. Two newlines are one blank
        # line, so the blank count is one less than the run length.
        run = 1
        for raw_seg in reversed(context.raw_stack):
            if raw_seg.is_type("newline"):
                run += 1
            elif raw_seg.is_type("whitespace"):
                continue
            else:
                break
        blank_lines = run - 1

        if blank_lines >= minimum:
            return None

        return [
            LintResult(
                anchor=context.segment,
                fixes=[
                    LintFix.create_after(
                        context.segment,
                        [NewlineSegment() for _ in range(minimum - blank_lines)],
                    )
                ],
                description=(
                    f"Expected at least {minimum} blank line(s) between statements, "
                    f"found {blank_lines}."
                ),
            )
        ]
