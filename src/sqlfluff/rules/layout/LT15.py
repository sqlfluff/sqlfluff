"""Implementation of Rule LT15."""

from enum import Enum
from typing import List, Optional, Tuple

from sqlfluff.core.parser import NewlineSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class _Scope(Enum):
    """Where in the file a gap sits, which decides whose limit applies.

    The three scopes are the ones the maximum has always distinguished; naming
    them lets the minimum resolve the same way instead of keeping a second,
    slightly different copy of the logic.
    """

    INSIDE_STATEMENT = "inside a statement"
    BETWEEN_STATEMENTS = "between statements"
    BETWEEN_BATCHES = "between batches"


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
    unchanged. It applies only between statements, never inside one or between
    batches, matching the scope its name describes.

    .. note::

        ``minimum_empty_lines_between_statements`` is capped by
        ``maximum_empty_lines_between_statements``. The two settings validate
        independently, so a minimum above the maximum is accepted configuration,
        but no file can satisfy both: the minimum inserts blank lines and the
        maximum deletes them straight back, so ``sqlfluff fix`` alternates
        between the two results on every run instead of converging. Where the
        cap changes what would otherwise be reported, a warning is emitted
        naming both values.
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

        scope = self._resolve_scope(context)

        # Terminators are only sought for the same-line minimum check; none of the
        # maximum logic below applies to them.
        if context.segment.is_type("statement_terminator"):
            if scope is not _Scope.BETWEEN_STATEMENTS:
                return None
            return self._check_minimum(context, shares_line=True)

        # The minimum runs first because the two cannot both fire on one gap: one
        # wants newlines added, the other wants them removed.
        if scope is _Scope.BETWEEN_STATEMENTS:
            minimum_result = self._check_minimum(context, shares_line=False)
            if minimum_result:
                return minimum_result

        maximum_empty_lines = {
            _Scope.INSIDE_STATEMENT: self.maximum_empty_lines_inside_statements,
            _Scope.BETWEEN_STATEMENTS: self.maximum_empty_lines_between_statements,
            _Scope.BETWEEN_BATCHES: self.maximum_empty_lines_between_batches,
        }[scope]

        counted = self._count_blank_lines(context)
        if counted is None or counted[0] <= maximum_empty_lines:
            return None

        return [
            LintResult(
                anchor=context.segment,
                fixes=[LintFix.delete(context.segment)],
            )
        ]

    def _resolve_scope(self, context: RuleContext) -> _Scope:
        """Which of the three scopes this position sits in.

        Shared by the maximum's limit selection and the minimum's gate so the two
        cannot drift apart. Batches are detected structurally rather than by
        dialect name: the previous ``dialect.name == "tsql"`` test missed Oracle,
        which also has batch grammar, so a file-level gap there was measured
        against the between-statements maximum instead of the between-batches
        one. Testing for the node itself also means a dialect that gains batch
        grammar later needs no change here.
        """
        if any(seg.is_type("statement") for seg in context.parent_stack):
            # Directly inside a with_compound_statement (between CTEs, or between
            # the last CTE and the main query) uses the between-statements limit
            # to avoid conflicting with LT08, which requires blank lines
            # after CTEs.
            if context.parent_stack[-1].is_type("with_compound_statement"):
                return _Scope.BETWEEN_STATEMENTS
            return _Scope.INSIDE_STATEMENT

        if any(seg.is_type("batch") for seg in context.parent_stack):
            return _Scope.BETWEEN_STATEMENTS

        # File level: a gap out here separates batches in the dialects that have
        # them, and statements everywhere else.
        if any(
            seg.is_type("batch")
            for seg in (*context.siblings_pre, *context.siblings_post)
        ):
            return _Scope.BETWEEN_BATCHES
        return _Scope.BETWEEN_STATEMENTS

    def _count_blank_lines(self, context: RuleContext) -> Optional[Tuple[int, bool]]:
        """Blank lines in the run of newlines ending at the current segment.

        Both directions measure the gap with this, so they cannot disagree about
        what "two blank lines" means. Two consecutive newlines bound one blank
        line, hence the run length less one. Whitespace does not break the run,
        so a line of spaces still counts as blank.

        A templated newline ends the run rather than being counted: those lines
        are not in the source, so neither direction may add or remove them, and
        neither should let them stand in for lines the user wrote. Counting only
        as far as the nearest one leaves both directions measuring the same set
        of editable lines.

        Returns the count and whether the run was cut short by templated output.
        The maximum only ever deletes an editable newline, so the count alone is
        enough for it. The minimum has to add lines, and padding a gap whose
        rendered form already contains lines the source does not would be
        guessing at the result, so it declines those gaps entirely.

        Returns ``None`` when the anchor itself is templated, since there is then
        nothing editable to anchor a fix to.
        """
        if context.segment.is_templated:
            return None

        run = 1
        touched_templated = False
        for raw_seg in reversed(context.raw_stack):
            if raw_seg.is_type("newline"):
                if raw_seg.is_templated:
                    touched_templated = True
                    break
                run += 1
            elif raw_seg.is_type("whitespace"):
                continue
            else:
                break
        return run - 1, touched_templated

    def _effective_minimum(self) -> int:
        """The minimum actually enforced, capped by the maximum for the scope.

        See the note in the class docstring: uncapped, the two fixers undo each
        other and ``fix`` never converges.
        """
        return min(
            self.minimum_empty_lines_between_statements,
            self.maximum_empty_lines_between_statements,
        )

    def _is_gap_between_statements(
        self, context: RuleContext, *, shares_line: bool
    ) -> bool:
        """Whether the position is a gap with a statement on each side.

        A gap needs a statement on both sides, tested on the statement type
        rather than on any code. Without the preceding test, a file opening with
        a blank line or a comment reads as a gap before its first statement and
        gets padded. Without the following test, a batch delimiter (T-SQL ``GO``,
        Oracle ``/``) reads as the next statement and the rule demands a blank
        line in front of it; those are ``go_statement`` and
        ``slash_buffer_executor``, and they end a batch rather than starting one.
        """
        following = [
            seg
            for seg in context.siblings_post
            if not seg.is_type("dedent", "indent", "whitespace")
        ]

        if shares_line:
            # Whitespace and trailing comments are skipped rather than treated as
            # the end of the search: `SELECT a; -- x` still ends its line at the
            # newline after the comment, so stopping at the comment would report a
            # shared line that is not shared and tear the comment off it.
            for seg in following:
                if seg.is_type("comment", "inline_comment", "block_comment"):
                    continue
                # A newline already separates the statements, so the run-based
                # path owns this gap.
                if seg.is_type("newline"):
                    return False
                # A template tag in the gap is not a statement sharing the line,
                # and its surrounding whitespace is not the user's to rewrite.
                if seg.is_type("placeholder"):
                    return False
                break
        else:
            # Only act on the last newline of the run, or the same gap is
            # reported once per newline in it.
            if following and following[0].is_type("newline"):
                return False

        if not any(seg.is_type("statement") for seg in context.siblings_pre):
            return False
        if not any(seg.is_type("statement") for seg in following):
            return False

        # A template block start/end sits in the gap as a placeholder meta. The
        # newlines either side of it are not a gap between two statements, so
        # padding them puts blank lines around the tag rather than between the
        # statements, and the tag is not the user's line to move.
        for seg in reversed(context.siblings_pre):
            if seg.is_code:
                break
            if seg.is_type("placeholder"):
                return False
        for seg in context.siblings_post:
            if seg.is_code:
                break
            if seg.is_type("placeholder"):
                return False

        return True

    def _check_minimum(
        self, context: RuleContext, *, shares_line: bool
    ) -> Optional[List[LintResult]]:
        """Require at least ``minimum_empty_lines_between_statements`` blank lines.

        Handles both shapes a too-small gap can take. Usually there is a run of
        newlines to measure and pad. When the statements share a line
        (``SELECT a; SELECT b;``) there is no newline to crawl at all, so the run
        cannot be measured, the gap is zero by definition, and the fix has to
        create the line break as well as the blank lines.
        """
        minimum = self._effective_minimum()
        if not minimum:
            return None

        if not self._is_gap_between_statements(context, shares_line=shares_line):
            return None

        if shares_line:
            # No run to measure, so the templated check that the counter performs
            # for the other path has to happen here instead.
            if context.segment.is_templated:
                return None
            blank_lines = 0
            # One extra newline ends the first statement's line; the rest are the
            # blank lines themselves.
            newlines_to_add = minimum + 1
        else:
            counted = self._count_blank_lines(context)
            if counted is None:
                # Templated anchor: not ours to rewrite.
                return None
            blank_lines, touched_templated = counted
            if touched_templated or blank_lines >= minimum:
                return None
            newlines_to_add = minimum - blank_lines

        self._warn_if_capped()

        fixes = [
            LintFix.create_after(
                context.segment,
                [NewlineSegment() for _ in range(newlines_to_add)],
            )
        ]
        if shares_line:
            # Drop the space that separated the statements; it would otherwise be
            # left indenting the statement now starting the line.
            for seg in (
                s for s in context.siblings_post if not s.is_type("dedent", "indent")
            ):
                if seg.is_type("whitespace"):
                    fixes.append(LintFix.delete(seg))
                else:
                    break

        description = (
            f"Expected at least {minimum} blank line(s) between statements, "
            f"found {blank_lines}."
        )
        if shares_line:
            description = (
                f"Expected at least {minimum} blank line(s) between statements, "
                "found 0 (statements share a line)."
            )

        return [
            LintResult(
                anchor=context.segment,
                fixes=fixes,
                description=description,
            )
        ]

    def _warn_if_capped(self) -> None:
        """Tell the user when the cap is what decided the reported gap.

        Only fires where it changes an actual result, so a contradictory config
        that never meets two statements stays quiet.
        """
        configured = self.minimum_empty_lines_between_statements
        maximum = self.maximum_empty_lines_between_statements
        if configured > maximum:
            self.logger.warning(
                "minimum_empty_lines_between_statements (%s) is greater than "
                "maximum_empty_lines_between_statements (%s); enforcing %s. No "
                "file can satisfy both, and applying the minimum as configured "
                "would leave `sqlfluff fix` alternating between the two results "
                "instead of converging.",
                configured,
                maximum,
                maximum,
            )
