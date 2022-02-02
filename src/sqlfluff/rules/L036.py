"""Implementation of Rule L036."""

from typing import List, NamedTuple, Optional

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.parser import BaseSegment, NewlineSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import Segments
import sqlfluff.core.rules.functional.segment_predicates as sp


class SelectTargetsInfo(NamedTuple):
    """Info about select targets and nearby whitespace."""

    select_idx: int
    first_new_line_idx: int
    first_select_target_idx: int
    first_whitespace_idx: int
    select_targets: List[BaseSegment]
    from_segment: Optional[BaseSegment]
    pre_from_whitespace: List[BaseSegment]


@document_fix_compatible
class Rule_L036(BaseRule):
    """Select targets should be on a new line unless there is only one select target.

    .. note::
       A wildcard is (``SELECT *``) is not considered a single select target so
       always requires a new line.

    **Anti-pattern**

    Multiple select targets on the same line.

    .. code-block:: sql
        :force:

        select a, b
        from foo

        -- Single select target on its own line.

        SELECT
            a
        FROM foo


    **Best practice**

    Multiple select targets each on their own line.

    .. code-block:: sql
        :force:

        select
            a,
            b
        from foo

        -- Single select target on the same line as the ``SELECT``
        -- keyword.

        SELECT a
        FROM foo

    """

    def _eval(self, context: RuleContext):
        if context.segment.is_type("select_clause"):
            select_targets_info = self._get_indexes(context)
            if len(select_targets_info.select_targets) == 1:
                return self._eval_single_select_target_element(
                    select_targets_info,
                    context.functional.segment,
                    context.parent_stack,
                )
            elif len(select_targets_info.select_targets) > 1:
                return self._eval_multiple_select_target_elements(
                    select_targets_info, context.segment
                )

    @staticmethod
    def _get_indexes(context: RuleContext):
        children = context.functional.segment.children()
        select_targets = children.select(sp.is_type("select_clause_element"))
        first_select_target_idx = children.find(select_targets.get())
        selects = children.select(sp.is_keyword("select"))
        select_idx = children.find(selects.get())
        newlines = children.select(sp.is_type("newline"))
        first_new_line_idx = children.find(newlines.get())
        first_whitespace_idx = -1
        if first_new_line_idx != -1:
            # TRICKY: Ignore whitespace prior to the first newline, e.g. if
            # the line with "SELECT" (before any select targets) has trailing
            # whitespace.
            segments_after_first_line = children.select(
                sp.is_type("whitespace"), start_seg=children[first_new_line_idx]
            )
            first_whitespace_idx = children.find(segments_after_first_line.get())

        siblings_post = context.functional.siblings_post
        from_segment = siblings_post.first(sp.is_type("from_clause")).first().get()
        pre_from_whitespace = siblings_post.select(
            sp.is_type("whitespace"), stop_seg=from_segment
        )
        return SelectTargetsInfo(
            select_idx,
            first_new_line_idx,
            first_select_target_idx,
            first_whitespace_idx,
            select_targets,
            from_segment,
            list(pre_from_whitespace),
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
                fixes += [LintFix.delete(ws) for ws in ws_to_delete]
                fixes.append(LintFix.create_before(select_target, [NewlineSegment()]))

            # If we are at the last select target check if the FROM clause
            # is on the same line, and if so move it to its own line.
            if select_targets_info.from_segment:
                if (i + 1 == len(select_targets_info.select_targets)) and (
                    select_target.pos_marker.working_line_no
                    == select_targets_info.from_segment.pos_marker.working_line_no
                ):
                    fixes.extend(
                        [
                            LintFix.delete(ws)
                            for ws in select_targets_info.pre_from_whitespace
                        ]
                    )
                    fixes.append(
                        LintFix.create_before(
                            select_targets_info.from_segment,
                            [NewlineSegment()],
                        )
                    )

        if fixes:
            return LintResult(anchor=segment, fixes=fixes)

    def _eval_single_select_target_element(
        self, select_targets_info, select_clause: Segments, parent_stack
    ):
        wildcards = select_clause.children(
            sp.is_type("select_clause_element")
        ).children(sp.is_type("wildcard_expression"))
        is_wildcard = bool(wildcards)
        if is_wildcard:
            wildcard_select_clause_element = wildcards[0]

        if (
            select_targets_info.select_idx
            < select_targets_info.first_new_line_idx
            < select_targets_info.first_select_target_idx
        ) and (not is_wildcard):
            # Do we have a modifier?
            select_children = select_clause.children()
            modifier: Optional[Segments]
            modifier = select_children.first(sp.is_type("select_clause_modifier"))

            # Prepare the select clause which will be inserted
            # In most (but not all) case we'll want to replace the newline with
            # the statement and a newline, but in some cases however (see #1424)
            # we don't need the final newline.
            copy_with_newline = True
            insert_buff = [
                WhitespaceSegment(),
                select_children[select_targets_info.first_select_target_idx],
            ]

            # Check if the modifier is one we care about
            if modifier:
                # If it's already on the first line, ignore it.
                if (
                    select_children.index(modifier.get())
                    < select_targets_info.first_new_line_idx
                ):
                    modifier = None
            fixes = [
                # Delete the first select target from its original location.
                # We'll add it to the right section at the end, once we know
                # what to add.
                LintFix.delete(
                    select_children[select_targets_info.first_select_target_idx],
                ),
            ]

            # If we have a modifier to move:
            if modifier:

                # Add it to the insert
                insert_buff = [WhitespaceSegment(), modifier[0]] + insert_buff

                modifier_idx = select_children.index(modifier.get())
                # Delete the whitespace after it (which is two after, thanks to indent)
                if (
                    len(select_children) > modifier_idx + 1
                    and select_children[modifier_idx + 2].is_whitespace
                ):
                    fixes += [
                        LintFix.delete(
                            select_children[modifier_idx + 2],
                        ),
                    ]

                # Delete the modifier itself
                fixes += [
                    LintFix.delete(
                        modifier[0],
                    ),
                ]

                # Set the position marker for removing the preceding
                # whitespace and newline, which we'll use below.
                start_idx = modifier_idx
            else:
                # Set the position marker for removing the preceding
                # whitespace and newline, which we'll use below.
                start_idx = select_targets_info.first_select_target_idx

            if parent_stack and parent_stack[-1].is_type("select_statement"):
                select_stmt = parent_stack[-1]
                select_clause_idx = select_stmt.segments.index(select_clause.get())
                after_select_clause_idx = select_clause_idx + 1
                if len(select_stmt.segments) > after_select_clause_idx:
                    if select_stmt.segments[after_select_clause_idx].is_type("newline"):
                        # Since we're deleting the newline, we should also delete all
                        # whitespace before it or it will add random whitespace to
                        # following statements. So walk back through the segment
                        # deleting whitespace until you get the previous newline, or
                        # something else.
                        to_delete = select_children.reversed().select(
                            loop_while=sp.is_type("whitespace"),
                            start_seg=select_children[start_idx],
                        )
                        fixes += [LintFix.delete(seg) for seg in to_delete]

                        # The select_clause is immediately followed by a
                        # newline. Delete the newline in order to avoid leaving
                        # behind an empty line after fix, *unless* we stopped
                        # due to something other than a newline.
                        delete_last_newline = select_children[
                            start_idx - len(to_delete) - 1
                        ].is_type("newline")

                        # Delete the newline if we decided to.
                        if delete_last_newline:
                            fixes.append(
                                LintFix.delete(
                                    select_stmt.segments[after_select_clause_idx],
                                )
                            )

                    elif select_stmt.segments[after_select_clause_idx].is_type(
                        "whitespace"
                    ):
                        # The select_clause has stuff after (most likely a comment)
                        # Delete the whitespace immediately after the select clause
                        # so the other stuff aligns nicely based on where the select
                        # clause started
                        fixes += [
                            LintFix.delete(
                                select_stmt.segments[after_select_clause_idx],
                            ),
                        ]
                    elif select_stmt.segments[after_select_clause_idx].is_type(
                        "dedent"
                    ):
                        # The end of the select statement, so this is the one
                        # case we don't want the newline added to end of
                        # select_clause (see #1424)
                        copy_with_newline = False

                        # Again let's strip back the whitespace, but simpler
                        # as don't need to worry about new line so just break
                        # if see non-whitespace
                        to_delete = select_children.reversed().select(
                            loop_while=sp.is_type("whitespace"),
                            start_seg=select_children[select_clause_idx - 1],
                        )
                        fixes += [LintFix.delete(seg) for seg in to_delete]

                        # If we stopped due to something other than a newline,
                        # we want to keep the final newline.
                        copy_with_newline = not select_children[
                            select_clause_idx - len(to_delete) - 2
                        ].is_type("newline")

            if copy_with_newline:
                insert_buff = insert_buff + [NewlineSegment()]

            fixes += [
                # Insert the select_clause in place of the first newlin in the
                # Select statement
                LintFix.replace(
                    select_children[select_targets_info.first_new_line_idx],
                    insert_buff,
                ),
            ]

            return LintResult(
                anchor=select_clause.get(),
                fixes=fixes,
            )

        # If we have a wildcard on the same line as the FROM keyword, but not the same
        # line as the SELECT keyword, we need to move the FROM keyword to its own line.
        # i.e.
        # SELECT
        #   * FROM foo
        if select_targets_info.from_segment:
            if (
                is_wildcard
                and (
                    select_clause[0].pos_marker.working_line_no
                    != select_targets_info.from_segment.pos_marker.working_line_no
                )
                and (
                    wildcard_select_clause_element.pos_marker.working_line_no
                    == select_targets_info.from_segment.pos_marker.working_line_no
                )
            ):
                fixes = [
                    LintFix.delete(ws) for ws in select_targets_info.pre_from_whitespace
                ]
                fixes.append(
                    LintFix.create_before(
                        select_targets_info.from_segment,
                        [NewlineSegment()],
                    )
                )
                return LintResult(anchor=select_clause.get(), fixes=fixes)

        return None
