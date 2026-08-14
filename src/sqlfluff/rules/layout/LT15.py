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
    # Statement terminators are sought as well as newlines: a minimum between
    # statements has to be enforceable when the statements share a line, where
    # there is no newline to crawl at all.
    crawl_behaviour = SegmentSeekerCrawler(
        types={"newline", "statement_terminator"}, provide_raw_stack=True
    )
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """There should be a maximum number of empty lines."""
        self.maximum_empty_lines_between_statements: int
        self.maximum_empty_lines_inside_statements: int
        self.maximum_empty_lines_between_batches: int
        self.minimum_empty_lines_between_statements: int
        context_seg = context.segment

        # Terminators are only sought for the same-line minimum check; none of the
        # maximum logic below applies to them. The same outer-statement guard as
        # the newline path applies: a semicolon delimiting inner statements of a
        # compound or procedural body is not a gap between top-level statements.
        if context_seg.is_type("statement_terminator"):
            if any(seg.is_type("statement") for seg in context.parent_stack):
                return None
            return self._check_minimum_same_line(context)

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

        # A gap needs a statement on both sides. Without the preceding check, a
        # file that opens with a blank line or a comment is treated as a gap
        # before its first statement and padded, which is a false positive.
        if not any(seg.is_code for seg in context.siblings_pre):
            return None

        # Skip when nothing but the end of the file follows, so there is no gap to
        # pad, and when the newline is templated, since that is not ours to rewrite.
        if context.segment.is_templated or not any(
            seg.is_code for seg in context.siblings_post
        ):
            return None

        # A template block start/end sits in the gap as a placeholder meta. The
        # newlines either side of it are not a gap between two statements, so
        # padding them puts blank lines around the tag rather than between the
        # statements, and the tag is not the user's line to move.
        for seg in reversed(context.siblings_pre):
            if seg.is_code:
                break
            if seg.is_type("placeholder"):
                return None
        for seg in context.siblings_post:
            if seg.is_code:
                break
            if seg.is_type("placeholder"):
                return None

        # Count the run of newlines ending at this one. Two newlines are one blank
        # line, so the blank count is one less than the run length.
        run = 1
        for raw_seg in reversed(context.raw_stack):
            if raw_seg.is_type("newline"):
                # Only block tags leave a placeholder behind. A variable or macro
                # expanding to text containing newlines produces plain newline
                # segments with no placeholder, so the skip above does not see it
                # and this is the only guard against counting lines that are not
                # in the source. The maximum branch bails on the same condition.
                if raw_seg.is_templated:
                    return None
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

    def _check_minimum_same_line(
        self, context: RuleContext
    ) -> Optional[List[LintResult]]:
        """Enforce the minimum when two statements share a line.

        ``_check_minimum`` measures a run of newlines, so it can only fire where a
        newline exists. ``SELECT a; SELECT b;`` has none between the statements, so
        the gap was accepted however the minimum was configured. Here the break
        itself is missing, and the fix has to create it as well as the blank lines.
        """
        minimum = self.minimum_empty_lines_between_statements
        if not minimum:
            return None

        if context.segment.is_templated:
            return None

        following = [
            seg for seg in context.siblings_post if not seg.is_type("dedent", "indent")
        ]
        # A newline already separates the statements, so the run-based check owns
        # this gap. Whitespace and trailing comments are skipped rather than
        # treated as the end of the search: `SELECT a; -- x` still ends its line
        # at the newline after the comment, and stopping at the comment would
        # report a shared line that is not shared and tear the comment off it.
        for seg in following:
            if seg.is_type("whitespace", "comment", "inline_comment", "block_comment"):
                continue
            if seg.is_type("newline"):
                return None
            # A template tag in the gap is not a statement sharing the line, and
            # its surrounding whitespace is not the user's to rewrite.
            if seg.is_type("placeholder"):
                return None
            break

        # Nothing but the end of the file follows, so there is no gap to pad.
        if not any(seg.is_code for seg in following):
            return None

        # No line break at all, so every required blank line is missing and the
        # break that ends this statement's line is missing too.
        fixes = [
            LintFix.create_after(
                context.segment,
                [NewlineSegment() for _ in range(minimum + 1)],
            )
        ]
        # Drop the space that separated the statements; it would otherwise be left
        # indenting the statement now starting the line.
        for seg in following:
            if seg.is_type("whitespace"):
                fixes.append(LintFix.delete(seg))
            else:
                break

        return [
            LintResult(
                anchor=context.segment,
                fixes=fixes,
                description=(
                    f"Expected at least {minimum} blank line(s) between statements, "
                    "found 0 (statements share a line)."
                ),
            )
        ]
