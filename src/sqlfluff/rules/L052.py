"""Implementation of Rule L052."""
from typing import List, Optional

from sqlfluff.core.parser import SymbolSegment
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import NewlineSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)


@document_configuration
@document_fix_compatible
class Rule_L052(BaseRule):
    """Statements must end with a semi-colon.

    | **Anti-pattern**
    | A statement is not immediately terminated with a semi-colon, the • represents space.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo

        ;

        SELECT
            b
        FROM bar••;

    | **Best practice**
    | Immediately terminate the statement with a semi-colon.

    .. code-block:: sql
       :force:

        SELECT
            a
        FROM foo;
    """

    config_keywords = ["multiline_newline", "require_final_semicolon"]

    @staticmethod
    def _handle_preceding_inline_comments(pre_semicolon_segments, anchor_segment):
        """Adjust pre_semicolon_segments and anchor_segment to not move preceding inline comments.

        We don't want to move inline comments that are on the same line
        as the preceding code segment as they could contain noqa instructions.
        """
        # See if we have a preceding inline comment on the same line as the preceding segment.
        same_line_comment = next(
            (
                s
                for s in pre_semicolon_segments
                if s.is_comment
                and s.name != "block_comment"
                and s.pos_marker.working_line_no
                == anchor_segment.pos_marker.working_line_no
            ),
            None,
        )
        # If so then make that our new anchor segment and adjust
        # pre_semicolon_segments accordingly.
        if same_line_comment:
            anchor_segment = same_line_comment
            pre_semicolon_segments = pre_semicolon_segments[
                : pre_semicolon_segments.index(same_line_comment)
            ]

        return pre_semicolon_segments, anchor_segment

    @staticmethod
    def _handle_trailing_inline_comments(context, anchor_segment):
        """Adjust anchor_segment to not move trailing inline comment.

        We don't want to move inline comments that are on the same line
        as the preceding code segment as they could contain noqa instructions.
        """
        # See if we have a trailing inline comment on the same line as the preceding segment.
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
                for s in context.parent_stack[0].path_to(segment)
                if s.is_type("statement")
            ),
            None,
        )
        if statement_segment is None:  # pragma: no cover
            # If we can't find a parent statement segment then don't try anything special.
            return False

        if not any(statement_segment.recursive_crawl("newline")):
            # Statement segment has no newlines therefore starts and ends on the same line.
            return True

        return False

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Statements must end with a semi-colon."""
        # Config type hints
        self.multiline_newline: bool
        self.require_final_semicolon: bool

        # First we can simply handle the case of existing semi-colon alignment.
        if context.segment.name == "semicolon":

            # Locate semicolon and iterate back over the raw stack
            # to find the end of the preceding statement.
            anchor_segment = context.segment
            is_one_line = False
            pre_semicolon_segments = []
            for segment in context.raw_stack[::-1]:
                if segment.is_code:
                    is_one_line = self._is_one_line_statement(context, segment)
                    break
                elif not segment.is_meta:
                    pre_semicolon_segments.append(segment)
                anchor_segment = segment

            # We can tidy up any whitespace between the semi-colon
            # and the preceding code/comment segment.
            # Don't mess with comment spacing/placement.
            whitespace_deletions = []
            for segment in pre_semicolon_segments:
                if not segment.is_whitespace:
                    break
                whitespace_deletions.append(segment)

            semicolon_newline = self.multiline_newline if not is_one_line else False

            # Semi-colon on same line.
            if not semicolon_newline:
                if len(pre_semicolon_segments) >= 1:
                    # If preceding segments are found then delete the old
                    # semi-colon and its preceding whitespace and then insert
                    # the semi-colon in the correct location.
                    fixes = [
                        LintFix.replace(
                            anchor_segment,
                            [
                                anchor_segment,
                                SymbolSegment(raw=";", type="symbol", name="semicolon"),
                            ],
                        ),
                        LintFix.delete(
                            context.segment,
                        ),
                    ]
                    fixes.extend(LintFix.delete(d) for d in whitespace_deletions)
                    return LintResult(
                        anchor=anchor_segment,
                        fixes=fixes,
                    )
            # Semi-colon on new line.
            else:
                # Adjust pre_semicolon_segments and anchor_segment for preceding inline comments.
                # Inline comments can contain noqa logic so we need to add the newline after the inline comment.
                (
                    pre_semicolon_segments,
                    anchor_segment,
                ) = self._handle_preceding_inline_comments(
                    pre_semicolon_segments, anchor_segment
                )

                if not (
                    (len(pre_semicolon_segments) == 1)
                    and all(s.is_type("newline") for s in pre_semicolon_segments)
                ):
                    # If preceding segment is not a single newline then delete the old
                    # semi-colon/preceding whitespace and then insert the
                    # semi-colon in the correct location.

                    # This handles an edge case in which an inline comment comes after the semi-colon.
                    anchor_segment = self._handle_trailing_inline_comments(
                        context, anchor_segment
                    )

                    fixes = [
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
                    fixes.extend(LintFix.delete(d) for d in whitespace_deletions)
                    return LintResult(
                        anchor=anchor_segment,
                        fixes=fixes,
                    )

        # SQL does not require a final trailing semi-colon, however
        # this rule looks to enforce that it is there.
        if self.require_final_semicolon:
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
            pre_semicolon_segments = []
            for segment in complete_stack[::-1]:  # type: ignore
                if segment.name == "semicolon":
                    semi_colon_exist_flag = True
                elif segment.is_code:
                    is_one_line = self._is_one_line_statement(context, segment)
                    break
                elif not segment.is_meta:
                    pre_semicolon_segments.append(segment)
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
                    # Adjust pre_semicolon_segments and anchor_segment for inline comments.
                    (
                        pre_semicolon_segments,
                        anchor_segment,
                    ) = self._handle_preceding_inline_comments(
                        pre_semicolon_segments, anchor_segment
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
