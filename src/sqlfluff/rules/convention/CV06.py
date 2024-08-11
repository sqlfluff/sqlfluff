"""Implementation of Rule CV06."""

from typing import List, NamedTuple, Optional, Sequence, cast

from sqlfluff.core.parser import BaseSegment, NewlineSegment, RawSegment, SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.functional import Segments, sp


class SegmentMoveContext(NamedTuple):
    """Context information for moving a segment."""

    anchor_segment: RawSegment
    is_one_line: bool
    before_segment: Segments
    whitespace_deletions: Segments


class Rule_CV06(BaseRule):
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

    name = "convention.terminator"
    aliases = ("L052",)
    groups = ("all", "convention")
    config_keywords = ["multiline_newline", "require_final_semicolon"]
    crawl_behaviour = RootOnlyCrawler()
    is_fix_compatible = True

    @staticmethod
    def _handle_preceding_inline_comments(
        before_segment: Sequence[BaseSegment], anchor_segment: BaseSegment
    ):
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
                and not s.is_type("block_comment")
                and s.pos_marker
                and s.pos_marker.working_line_no
                # We don't need to handle the case where raw_segments is empty
                # because it never is. It's either a segment with raw children
                # or a raw segment which returns [self] as raw_segments.
                == anchor_segment.raw_segments[-1].pos_marker.working_line_no
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
    def _handle_trailing_inline_comments(
        parent_segment: BaseSegment, anchor_segment: BaseSegment
    ) -> BaseSegment:
        """Adjust anchor_segment to not move trailing inline comment.

        We don't want to move inline comments that are on the same line
        as the preceding code segment as they could contain noqa instructions.
        """
        # See if we have a trailing inline comment on the same line as the preceding
        # segment.
        for comment_segment in parent_segment.recursive_crawl("comment"):
            assert comment_segment.pos_marker
            assert anchor_segment.pos_marker
            if (
                comment_segment.pos_marker.working_line_no
                == anchor_segment.pos_marker.working_line_no
            ) and (not comment_segment.is_type("block_comment")):
                anchor_segment = comment_segment

        return anchor_segment

    @staticmethod
    def _is_one_line_statement(
        parent_segment: BaseSegment, segment: BaseSegment
    ) -> bool:
        """Check if the statement containing the provided segment is one line."""
        # Find statement segment containing the current segment.
        statement_segment = next(
            (
                ps.segment
                for ps in (parent_segment.path_to(segment) or [])
                if ps.segment.is_type("statement")
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

    def _get_segment_move_context(
        self, target_segment: RawSegment, parent_segment: BaseSegment
    ) -> SegmentMoveContext:
        # Locate the segment to be moved (i.e. context.segment) and search back
        # over the raw stack to find the end of the preceding statement.
        reversed_raw_stack = Segments(*parent_segment.raw_segments).reversed()
        before_code = reversed_raw_stack.select(
            loop_while=sp.not_(sp.is_code()), start_seg=target_segment
        )
        before_segment = before_code.select(sp.not_(sp.is_meta()))
        # We're selecting from the raw stack, so we know that before_code is
        # made of RawSegment elements.
        anchor_segment = (
            cast(RawSegment, before_code[-1]) if before_code else target_segment
        )
        first_code = reversed_raw_stack.select(
            sp.is_code(), start_seg=target_segment
        ).first()
        self.logger.debug("Semicolon: first_code: %s", first_code)
        is_one_line = (
            self._is_one_line_statement(parent_segment, first_code[0])
            if first_code
            else False
        )

        # We can tidy up any whitespace between the segment
        # and the preceding code/comment segment.
        # Don't mess with comment spacing/placement.
        whitespace_deletions = before_segment.select(loop_while=sp.is_whitespace())
        return SegmentMoveContext(
            anchor_segment, is_one_line, before_segment, whitespace_deletions
        )

    def _handle_semicolon(
        self, target_segment: RawSegment, parent_segment: BaseSegment
    ) -> Optional[LintResult]:
        info = self._get_segment_move_context(target_segment, parent_segment)
        semicolon_newline = self.multiline_newline if not info.is_one_line else False
        self.logger.debug("Semicolon Newline: %s", semicolon_newline)

        # Semi-colon on same line.
        if not semicolon_newline:
            return self._handle_semicolon_same_line(
                target_segment, parent_segment, info
            )
        # Semi-colon on new line.
        else:
            return self._handle_semicolon_newline(target_segment, parent_segment, info)

    def _handle_semicolon_same_line(
        self,
        target_segment: RawSegment,
        parent_segment: BaseSegment,
        info: SegmentMoveContext,
    ) -> Optional[LintResult]:
        if not info.before_segment:
            return None

        # If preceding segments are found then delete the old
        # semi-colon and its preceding whitespace and then insert
        # the semi-colon in the correct location.
        fixes = self._create_semicolon_and_delete_whitespace(
            target_segment,
            parent_segment,
            info.anchor_segment,
            info.whitespace_deletions,
            [
                SymbolSegment(raw=";", type="statement_terminator"),
            ],
        )
        return LintResult(
            anchor=info.anchor_segment,
            fixes=fixes,
        )

    def _handle_semicolon_newline(
        self,
        target_segment: RawSegment,
        parent_segment: BaseSegment,
        info: SegmentMoveContext,
    ) -> Optional[LintResult]:
        # Adjust before_segment and anchor_segment for preceding inline
        # comments. Inline comments can contain noqa logic so we need to add the
        # newline after the inline comment.
        (before_segment, anchor_segment) = self._handle_preceding_inline_comments(
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
        anchor_segment = self._handle_trailing_inline_comments(
            parent_segment, anchor_segment
        )
        fixes = []
        if anchor_segment is target_segment:
            fixes.append(
                LintFix.replace(
                    anchor_segment,
                    [
                        NewlineSegment(),
                        SymbolSegment(raw=";", type="statement_terminator"),
                    ],
                )
            )
        else:
            fixes.extend(
                self._create_semicolon_and_delete_whitespace(
                    target_segment,
                    parent_segment,
                    anchor_segment,
                    info.whitespace_deletions,
                    [
                        NewlineSegment(),
                        SymbolSegment(raw=";", type="statement_terminator"),
                    ],
                )
            )
        return LintResult(
            anchor=anchor_segment,
            fixes=fixes,
        )

    def _create_semicolon_and_delete_whitespace(
        self,
        target_segment: BaseSegment,
        parent_segment: BaseSegment,
        anchor_segment: BaseSegment,
        whitespace_deletions: Segments,
        create_segments: List[BaseSegment],
    ) -> List[LintFix]:
        anchor_segment = self._choose_anchor_segment(
            parent_segment, "create_after", anchor_segment, filter_meta=True
        )
        lintfix_fn = LintFix.create_after
        whitespace_deletion_set = set(whitespace_deletions)
        if anchor_segment in whitespace_deletion_set:
            # Can't delete() and create_after() the same segment. Use replace()
            # instead.
            lintfix_fn = LintFix.replace
            whitespace_deletions = whitespace_deletions.select(
                lambda seg: seg is not anchor_segment
            )
        fixes = [
            lintfix_fn(
                anchor_segment,
                create_segments,
            ),
            LintFix.delete(
                target_segment,
            ),
        ]
        fixes.extend(LintFix.delete(d) for d in whitespace_deletions)
        return fixes

    def _ensure_final_semicolon(
        self, parent_segment: BaseSegment
    ) -> Optional[LintResult]:
        # Iterate backwards over complete stack to find
        # if the final semi-colon is already present.
        anchor_segment = parent_segment.segments[-1]
        trigger_segment = parent_segment.segments[-1]
        semi_colon_exist_flag = False
        is_one_line = False
        before_segment = []
        for segment in parent_segment.segments[::-1]:
            anchor_segment = segment
            if segment.is_type("statement_terminator"):
                semi_colon_exist_flag = True
            elif segment.is_code:
                is_one_line = self._is_one_line_statement(parent_segment, segment)
                break
            elif not segment.is_meta:
                before_segment.append(segment)
            trigger_segment = segment
        else:
            return None  # File does not contain any statements
        self.logger.debug("Trigger on: %s", trigger_segment)
        self.logger.debug("Anchoring on: %s", anchor_segment)

        semicolon_newline = self.multiline_newline if not is_one_line else False

        if not semi_colon_exist_flag:
            # Create the final semi-colon if it does not yet exist.

            # Semi-colon on same line.
            if not semicolon_newline:
                fixes = [
                    LintFix.create_after(
                        self._choose_anchor_segment(
                            parent_segment,
                            "create_after",
                            anchor_segment,
                            filter_meta=True,
                        ),
                        [
                            SymbolSegment(raw=";", type="statement_terminator"),
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
                self.logger.debug("Revised anchor on: %s", anchor_segment)
                fixes = [
                    LintFix.create_after(
                        self._choose_anchor_segment(
                            parent_segment,
                            "create_after",
                            anchor_segment,
                            filter_meta=True,
                        ),
                        [
                            NewlineSegment(),
                            SymbolSegment(raw=";", type="statement_terminator"),
                        ],
                    )
                ]
            return LintResult(
                anchor=trigger_segment,
                fixes=fixes,
            )
        return None

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Statements must end with a semi-colon."""
        # Config type hints
        self.multiline_newline: bool
        self.require_final_semicolon: bool

        # We should only be dealing with a root segment
        assert context.segment.is_type("file")
        results = []
        for idx, seg in enumerate(context.segment.segments):
            res = None
            # First we can simply handle the case of existing semi-colon alignment.
            if seg.is_type("statement_terminator"):
                # If it's a terminator then we know it's a raw.
                seg = cast(RawSegment, seg)
                self.logger.debug("Handling semi-colon: %s", seg)
                res = self._handle_semicolon(seg, context.segment)
            # Otherwise handle the end of the file separately.
            elif (
                self.require_final_semicolon
                and idx == len(context.segment.segments) - 1
            ):
                self.logger.debug("Handling final segment: %s", seg)
                res = self._ensure_final_semicolon(context.segment)
            if res:
                results.append(res)

        return results
