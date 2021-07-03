"""Implementation of Rule L036."""

from typing import List, NamedTuple

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.parser import BaseSegment, NewlineSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


class SelectTargetsInfo(NamedTuple):
    """Info about select targets and nearby whitespace."""

    select_idx: int
    first_new_line_idx: int
    first_select_target_idx: int
    first_whitespace_idx: int
    select_targets: List[BaseSegment]


@document_fix_compatible
class Rule_L036(BaseRule):
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
            if seg.is_type("select_clause_element"):
                select_targets.append(seg)
                if first_select_target_idx == -1:
                    first_select_target_idx = fname_idx
            if seg.is_type("keyword") and seg.name == "select" and select_idx == -1:
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
        """Multiple select targets. Ensure each is on a separate line."""
        # Insert newline before every select target.
        fixes = []
        for i, select_target in enumerate(select_targets_info.select_targets):
            base_segment = (
                segment if not i else select_targets_info.select_targets[i - 1]
            )
            if (
                base_segment.pos_marker.working_line_no
                == select_target.pos_marker.working_line_no
            ):
                # Find and delete any whitespace before the select target.
                start_seg = select_targets_info.select_idx
                # If any select modifier (e.g. distinct ) is present, start
                # there rather than at the beginning.
                modifier = segment.get_child("select_clause_modifier")
                if modifier:
                    start_seg = segment.segments.index(modifier)

                ws_to_delete = segment.select_children(
                    start_seg=segment.segments[start_seg]
                    if not i
                    else select_targets_info.select_targets[i - 1],
                    select_if=lambda s: s.is_type("whitespace"),
                    loop_while=lambda s: s.is_type("whitespace", "comma") or s.is_meta,
                )
                fixes += [LintFix("delete", ws) for ws in ws_to_delete]
                fixes.append(LintFix("create", select_target, NewlineSegment()))
        if fixes:
            return LintResult(anchor=segment, fixes=fixes)

    def _eval_single_select_target_element(
        self, select_targets_info, select_clause, parent_stack
    ):
        is_wildcard = False
        for segment in select_clause.segments:
            if segment.is_type("select_clause_element"):
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
            # Do we have a modifier?
            modifier = select_clause.get_child("select_clause_modifier")

            # there is a newline between select and select target
            insert_buff = [
                WhitespaceSegment(),
                select_clause.segments[select_targets_info.first_select_target_idx],
                NewlineSegment(),
            ]

            # Also move any modifiers if present
            if modifier:
                # If it's already on the first line, ignore it.
                if (
                    select_clause.segments.index(modifier)
                    < select_targets_info.first_new_line_idx
                ):
                    modifier = None
                # Otherwise we need to move it too
                else:
                    insert_buff = [WhitespaceSegment(), modifier] + insert_buff

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

            # Also delete the original modifier if present
            if modifier:
                fixes += [
                    LintFix(
                        "delete",
                        modifier,
                    ),
                ]

            if (
                select_targets_info.first_select_target_idx
                - select_targets_info.first_new_line_idx
                == 2
                and select_clause.segments[
                    select_targets_info.first_new_line_idx + 1
                ].is_whitespace
            ):
                # If the select target is preceded by a single whitespace
                # segment, delete that as well. This addresses the bug fix
                # tested in L036.yml's "test_cte" scenario.
                fixes.append(
                    LintFix(
                        "delete",
                        select_clause.segments[
                            select_targets_info.first_new_line_idx + 1
                        ],
                    ),
                )
            if parent_stack and parent_stack[-1].is_type("select_statement"):
                select_stmt = parent_stack[-1]
                select_clause_idx = select_stmt.segments.index(select_clause)
                after_select_clause_idx = select_clause_idx + 1
                if len(select_stmt.segments) > after_select_clause_idx:
                    if select_stmt.segments[after_select_clause_idx].is_type("newline"):
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
