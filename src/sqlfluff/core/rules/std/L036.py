"""Implementation of Rule L036."""

from typing import List, NamedTuple

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


class SelectTargetsInfo(NamedTuple):
    """Info about select targets and nearby whitespace."""

    select_idx: int
    first_new_line_idx: int
    first_select_target_idx: int
    first_whitespace_idx: int
    select_targets: List[BaseSegment]


@document_fix_compatible
class Rule_L036(BaseCrawler):
    """Select targets should be on a new line unless there is only one select target.

    | **Anti-pattern**

    .. code-block:: sql

        select
            *
        from x


    | **Best practice**

    .. code-block:: sql

        select
            a,
            b,
            c
        from x

    """

    def _eval(self, segment, raw_stack, **kwargs):
        if segment.is_type("select_clause"):
            select_targets_info = self._get_indexes(segment)
            if len(select_targets_info.select_targets) == 1:
                parent_stack = kwargs.get("parent_stack")
                return self._eval_single_select_target_element(
                    select_targets_info, segment, parent_stack
                )
            elif len(select_targets_info.select_targets) > 1:
                return self._eval_multiple_select_target_elements(
                    select_targets_info, segment
                )

    @staticmethod
    def _get_indexes(segment):
        select_idx = -1
        first_new_line_idx = -1
        first_select_target_idx = -1
        first_whitespace_idx = -1
        select_targets = []
        for fname_idx, seg in enumerate(segment.segments):
            if seg.is_type("select_target_element"):
                select_targets.append(seg)
                if first_select_target_idx == -1:
                    first_select_target_idx = fname_idx
            if seg.is_type("keyword") and seg.name == "SELECT" and select_idx == -1:
                select_idx = fname_idx
            if seg.is_type("newline") and first_new_line_idx == -1:
                first_new_line_idx = fname_idx
            # TRICKY: Ignore whitespace prior to the first newline, e.g. if
            # the line with "SELECT" (before any select targets) has trailing
            # whitespace.
            if (
                seg.is_type("whitespace")
                and first_new_line_idx != -1
                and first_whitespace_idx == -1
            ):
                first_whitespace_idx = fname_idx

        return SelectTargetsInfo(
            select_idx,
            first_new_line_idx,
            first_select_target_idx,
            first_whitespace_idx,
            select_targets,
        )

    def _eval_multiple_select_target_elements(self, select_targets_info, segment):
        if select_targets_info.first_new_line_idx == -1:
            # there are multiple select targets but no new lines

            # Find and delete any whitespace between "SELECT" and its targets.
            ws_to_delete = segment.select_children(
                start_seg=segment.segments[select_targets_info.select_idx],
                select_if=lambda s: s.is_type("whitespace"),
                loop_while=lambda s: s.is_type("whitespace") or s.is_meta,
            )
            fixes = [LintFix("delete", ws) for ws in ws_to_delete]
            # Insert newline before the first select target.
            ins = self.make_newline(
                pos_marker=segment.pos_marker.advance_by(segment.raw)
            )
            fixes.append(LintFix("create", select_targets_info.select_targets[0], ins))
            return LintResult(anchor=segment, fixes=fixes)

    def _eval_single_select_target_element(
        self, select_targets_info, select_clause, parent_stack
    ):
        is_wildcard = False
        for segment in select_clause.segments:
            if segment.is_type("select_target_element"):
                for sub_segment in segment.segments:
                    if sub_segment.is_type("wildcard_expression"):
                        is_wildcard = True

        if is_wildcard:
            return None
        elif (
            select_targets_info.select_idx
            < select_targets_info.first_new_line_idx
            < select_targets_info.first_select_target_idx
        ):
            # there is a newline between select and select target
            insert_buff = [
                self.make_whitespace(
                    raw=" ",
                    pos_marker=select_clause.segments[
                        select_targets_info.first_new_line_idx
                    ].pos_marker,
                ),
                select_clause.segments[select_targets_info.first_select_target_idx],
                self.make_newline(
                    pos_marker=select_clause.segments[
                        select_targets_info.first_new_line_idx
                    ].pos_marker
                ),
            ]
            fixes = [
                # Replace "newline" with <<select_target>>, "newline".
                LintFix(
                    "edit",
                    select_clause.segments[select_targets_info.first_new_line_idx],
                    insert_buff,
                ),
                # Delete the first select target from its original location.
                LintFix(
                    "delete",
                    select_clause.segments[select_targets_info.first_select_target_idx],
                ),
            ]
            if parent_stack and parent_stack[-1].type == "select_statement":
                select_stmt = parent_stack[-1]
                select_clause_idx = select_stmt.segments.index(select_clause)
                after_select_clause_idx = select_clause_idx + 1
                if len(select_stmt.segments) > after_select_clause_idx:
                    if select_stmt.segments[after_select_clause_idx].type == "newline":
                        # The select_clause is immediately followed by a
                        # newline. Delete the newline in order to avoid leaving
                        # behind an empty line after fix.
                        fixes.append(
                            LintFix(
                                "delete", select_stmt.segments[after_select_clause_idx]
                            )
                        )
            return LintResult(
                anchor=select_clause,
                fixes=fixes,
            )
        else:
            return None
