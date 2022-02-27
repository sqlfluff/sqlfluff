"""Implementation of Rule L052."""
from typing import List, NamedTuple, Optional

from sqlfluff.core.parser import SymbolSegment
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import NewlineSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.core.rules.functional import Segments, sp


class SegmentMoveContext(NamedTuple):
    """Context information for moving a segment."""

    anchor_segment: BaseSegment
    is_one_line: bool
    before_segment: Segments
    whitespace_deletions: Segments


@document_configuration
@document_fix_compatible
class Rule_L052(BaseRule):
    """Statements must end with a semi-colon.

    **Anti-pattern**

    A statement is not immediately terminated with a semi-colon. The ``•`` represents
    space.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo

        ;

        SELECT
            b
        FROM bar••;

    **Best practice**

    Immediately terminate the statement with a semi-colon.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo;
    """

    config_keywords = ["multiline_newline", "require_final_semicolon"]

    @staticmethod
    def _handle_preceding_inline_comments(before_segment, anchor_segment):
        """Adjust segments to not move preceding inline comments.

        We don't want to move inline comments that are on the same line
        as the preceding code segment as they could contain noqa instructions.
        """
        # See if we have a preceding inline comment on the same line as the preceding
        # segment.
        same_line_comment = next(
            (
                s
                for s in before_segment
                if s.is_comment
                and s.name != "block_comment"
                and s.pos_marker.working_line_no
                == anchor_segment.pos_marker.working_line_no
            ),
            None,
        )
        # If so then make that our new anchor segment and adjust
        # before_segment accordingly.
        if same_line_comment:
            anchor_segment = same_line_comment
            before_segment = before_segment[: before_segment.index(same_line_comment)]

        return before_segment, anchor_segment

    @staticmethod
    def _handle_trailing_inline_comments(context, anchor_segment):
        """Adjust anchor_segment to not move trailing inline comment.

        We don't want to move inline comments that are on the same line
        as the preceding code segment as they could contain noqa instructions.
        """
        # See if we have a trailing inline comment on the same line as the preceding
        # segment.
        for parent_segment in context.parent_stack[::-1]:
            for comment_segment in parent_segment.recursive_crawl("comment"):
                if (
                    comment_segment.pos_marker.working_line_no
                    == anchor_segment.pos_marker.working_line_no
                ) and (comment_segment.name != "block_comment"):
                    anchor_segment = comment_segment

        return anchor_segment

    @staticmethod
    def _is_one_line_statement(context, segment):
        """Check if the statement containing the provided segment is one line."""
        # Find statement segment containing the current segment.
        statement_segment = next(
            (
                s
                for s in (context.parent_stack[0].path_to(segment) or [])
                if s.is_type("statement")
            ),
            None,
        )
        if statement_segment is None:  # pragma: no cover
            # If we can't find a parent statement segment then don't try anything
            # special.
            return False

        if not any(statement_segment.recursive_crawl("newline")):
            # Statement segment has no newlines therefore starts and ends on the same
            # line.
            return True

        return False

    def _get_segment_move_context(self, context: RuleContext) -> SegmentMoveContext:
        # Locate the segment to be moved (i.e. context.segment) and search back
        # over the raw stack to find the end of the preceding statement.
        reversed_raw_stack = context.functional.raw_stack.reversed()
        before_code = reversed_raw_stack.select(loop_while=sp.not_(sp.is_code()))
        before_segment = before_code.select(sp.not_(sp.is_meta()))
        anchor_segment = before_code[-1] if before_code else context.segment
        first_code = reversed_raw_stack.select(sp.is_code()).first()
        is_one_line = (
            self._is_one_line_statement(context, first_code[0]) if first_code else False
        )

        # We can tidy up any whitespace between the segment
        # and the preceding code/comment segment.
        # Don't mess with comment spacing/placement.
        whitespace_deletions = before_segment.select(loop_while=sp.is_whitespace())
        return SegmentMoveContext(
            anchor_segment, is_one_line, before_segment, whitespace_deletions
        )

    def _handle_semicolon(self, context: RuleContext) -> Optional[LintResult]:
        info = self._get_segment_move_context(context)
        semicolon_newline = self.multiline_newline if not info.is_one_line else False

        # Semi-colon on same line.
        if not semicolon_newline:
            return self._handle_semicolon_same_line(context, info)
        # Semi-colon on new line.
        else:
            return self._handle_semicolon_newline(context, info)

    @staticmethod
    def _handle_semicolon_same_line(
        context: RuleContext, info: SegmentMoveContext
    ) -> Optional[LintResult]:
        if not info.before_segment:
            return None

        # If preceding segments are found then delete the old
        # semi-colon and its preceding whitespace and then insert
        # the semi-colon in the correct location.
        fixes = [
            LintFix.replace(
                info.anchor_segment,
                [
                    info.anchor_segment,
                    SymbolSegment(raw=";", type="symbol", name="semicolon"),
                ],
            ),
            LintFix.delete(
                context.segment,
            ),
        ]
        fixes.extend(LintFix.delete(d) for d in info.whitespace_deletions)
        return LintResult(
            anchor=info.anchor_segment,
            fixes=fixes,
        )

    def _handle_semicolon_newline(
        self, context: RuleContext, info: SegmentMoveContext
    ) -> Optional[LintResult]:
        # Adjust before_segment and anchor_segment for preceding inline
        # comments. Inline comments can contain noqa logic so we need to add the
        # newline after the inline comment.
        (before_segment, anchor_segment,) = self._handle_preceding_inline_comments(
            info.before_segment, info.anchor_segment
        )

        if (len(before_segment) == 1) and all(
            s.is_type("newline") for s in before_segment
        ):
            return None

        # If preceding segment is not a single newline then delete the old
        # semi-colon/preceding whitespace and then insert the
        # semi-colon in the correct location.

        # This handles an edge case in which an inline comment comes after
        # the semi-colon.
        anchor_segment = self._handle_trailing_inline_comments(context, anchor_segment)
        fixes = []
        if anchor_segment is context.segment:
            fixes.append(
                LintFix.replace(
                    anchor_segment,
                    [
                        NewlineSegment(),
                        SymbolSegment(raw=";", type="symbol", name="semicolon"),
                    ],
                )
            )
        else:
            fixes.extend(
                [
                    LintFix.replace(
                        anchor_segment,
                        [
                            anchor_segment,
                            NewlineSegment(),
                            SymbolSegment(raw=";", type="symbol", name="semicolon"),
                        ],
                    ),
                    LintFix.delete(
                        context.segment,
                    ),
                ]
            )
            fixes.extend(LintFix.delete(d) for d in info.whitespace_deletions)
        return LintResult(
            anchor=anchor_segment,
            fixes=fixes,
        )

    def _ensure_final_semicolon(self, context: RuleContext) -> Optional[LintResult]:
        # Locate the end of the file.
        if not self.is_final_segment(context):
            return None

        # Include current segment for complete stack.
        complete_stack: List[BaseSegment] = list(context.raw_stack)
        complete_stack.append(context.segment)

        # Iterate backwards over complete stack to find
        # if the final semi-colon is already present.
        anchor_segment = context.segment
        semi_colon_exist_flag = False
        is_one_line = False
        before_segment = []
        for segment in complete_stack[::-1]:
            if segment.name == "semicolon":
                semi_colon_exist_flag = True
            elif segment.is_code:
                is_one_line = self._is_one_line_statement(context, segment)
                break
            elif not segment.is_meta:
                before_segment.append(segment)
            anchor_segment = segment

        semicolon_newline = self.multiline_newline if not is_one_line else False

        if not semi_colon_exist_flag:
            # Create the final semi-colon if it does not yet exist.

            # Semi-colon on same line.
            if not semicolon_newline:
                fixes = [
                    LintFix.replace(
                        anchor_segment,
                        [
                            anchor_segment,
                            SymbolSegment(raw=";", type="symbol", name="semicolon"),
                        ],
                    )
                ]
            # Semi-colon on new line.
            else:
                # Adjust before_segment and anchor_segment for inline
                # comments.
                (
                    before_segment,
                    anchor_segment,
                ) = self._handle_preceding_inline_comments(
                    before_segment, anchor_segment
                )
                fixes = [
                    LintFix.replace(
                        anchor_segment,
                        [
                            anchor_segment,
                            NewlineSegment(),
                            SymbolSegment(raw=";", type="symbol", name="semicolon"),
                        ],
                    )
                ]

            return LintResult(
                anchor=anchor_segment,
                fixes=fixes,
            )
        return None

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Statements must end with a semi-colon."""
        # Config type hints
        self.multiline_newline: bool
        self.require_final_semicolon: bool

        # First we can simply handle the case of existing semi-colon alignment.
        result = None
        if context.segment.name == "semicolon":
            result = self._handle_semicolon(context)
        elif self.require_final_semicolon:
            result = self._ensure_final_semicolon(context)

        return result
