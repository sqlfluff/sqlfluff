"""Implementation of Rule L036."""

from typing import List, NamedTuple, Optional, Sequence

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.parser import BaseSegment, NewlineSegment
from sqlfluff.core.parser.segments.base import IdentitySet
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.functional import Segments, sp, FunctionalContext


class SelectTargetsInfo(NamedTuple):
    """Info about select targets and nearby whitespace."""

    select_idx: int
    first_new_line_idx: int
    first_select_target_idx: int
    first_whitespace_idx: int
    comment_after_select_idx: int
    select_targets: Sequence[BaseSegment]
    from_segment: Optional[BaseSegment]
    pre_from_whitespace: List[BaseSegment]


@document_groups
@document_configuration
@document_fix_compatible
class Rule_L036(BaseRule):
    """Select targets should be on a new line unless there is only one select target.

    .. note::
       By default, a wildcard (e.g. ``SELECT *``) is considered a single select target.
       If you want it to be treated as multiple select targets, configure
       ``wildcard_policy = multiple``.

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

    groups = ("all",)
    config_keywords = ["wildcard_policy"]
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})

    def _eval(self, context: RuleContext):
        self.wildcard_policy: str
        assert context.segment.is_type("select_clause")
        select_targets_info = self._get_indexes(context)
        select_clause = FunctionalContext(context).segment
        wildcards = select_clause.children(
            sp.is_type("select_clause_element")
        ).children(sp.is_type("wildcard_expression"))
        has_wildcard = bool(wildcards)
        if len(select_targets_info.select_targets) == 1 and (
            not has_wildcard or self.wildcard_policy == "single"
        ):
            return self._eval_single_select_target_element(
                select_targets_info,
                context,
            )
        elif len(select_targets_info.select_targets):
            return self._eval_multiple_select_target_elements(
                select_targets_info, context.segment
            )

    @staticmethod
    def _get_indexes(context: RuleContext):
        children = FunctionalContext(context).segment.children()
        select_targets = children.select(sp.is_type("select_clause_element"))
        first_select_target_idx = children.find(select_targets.get())
        selects = children.select(sp.is_keyword("select"))
        select_idx = children.find(selects.get()) if selects else -1
        newlines = children.select(sp.is_type("newline"))
        first_new_line_idx = children.find(newlines.get()) if newlines else -1
        comment_after_select_idx = -1
        if newlines:
            comment_after_select = children.select(
                sp.is_type("comment"),
                start_seg=selects.get(),
                stop_seg=newlines.get(),
                loop_while=sp.or_(
                    sp.is_type("comment"), sp.is_type("whitespace"), sp.is_meta()
                ),
            )
            if comment_after_select:
                comment_after_select_idx = (
                    children.find(comment_after_select.get())
                    if comment_after_select
                    else -1
                )
        first_whitespace_idx = -1
        if first_new_line_idx != -1:
            # TRICKY: Ignore whitespace prior to the first newline, e.g. if
            # the line with "SELECT" (before any select targets) has trailing
            # whitespace.
            segments_after_first_line = children.select(
                sp.is_type("whitespace"), start_seg=children[first_new_line_idx]
            )
            first_whitespace_idx = children.find(segments_after_first_line.get())

        siblings_post = FunctionalContext(context).siblings_post
        from_segment = siblings_post.first(sp.is_type("from_clause")).first().get()
        pre_from_whitespace = siblings_post.select(
            sp.is_type("whitespace"), stop_seg=from_segment
        )
        return SelectTargetsInfo(
            select_idx,
            first_new_line_idx,
            first_select_target_idx,
            first_whitespace_idx,
            comment_after_select_idx,
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
        self, select_targets_info, context: RuleContext
    ):
        select_clause = FunctionalContext(context).segment
        parent_stack = context.parent_stack

        if (
            select_targets_info.select_idx
            < select_targets_info.first_new_line_idx
            < select_targets_info.first_select_target_idx
        ):
            # Do we have a modifier?
            select_children = select_clause.children()
            modifier: Optional[Segments]
            modifier = select_children.first(sp.is_type("select_clause_modifier"))

            # Prepare the select clause which will be inserted
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

                    def _fixes_for_move_after_select_clause(
                        stop_seg: BaseSegment,
                        delete_segments: Optional[Segments] = None,
                        add_newline: bool = True,
                    ) -> List[LintFix]:
                        """Cleans up by moving leftover select_clause segments.

                        Context: Some of the other fixes we make in
                        _eval_single_select_target_element() leave leftover
                        child segments that need to be moved to become
                        *siblings* of the select_clause.
                        """
                        start_seg = (
                            modifier[0]
                            if modifier
                            else select_children[select_targets_info.first_new_line_idx]
                        )
                        move_after_select_clause = select_children.select(
                            start_seg=start_seg,
                            stop_seg=stop_seg,
                        )
                        # :TRICKY: Below, we have a couple places where we
                        # filter to guard against deleting the same segment
                        # multiple times -- this is illegal.
                        # :TRICKY: Use IdentitySet rather than set() since
                        # different segments may compare as equal.
                        all_deletes = IdentitySet(
                            fix.anchor for fix in fixes if fix.edit_type == "delete"
                        )
                        fixes_ = []
                        for seg in delete_segments or []:
                            if seg not in all_deletes:
                                fixes.append(LintFix.delete(seg))
                                all_deletes.add(seg)
                        fixes_ += [
                            LintFix.delete(seg)
                            for seg in move_after_select_clause
                            if seg not in all_deletes
                        ]
                        fixes_.append(
                            LintFix.create_after(
                                select_clause[0],
                                ([NewlineSegment()] if add_newline else [])
                                + list(move_after_select_clause),
                            )
                        )
                        return fixes_

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
                        if to_delete:
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

                            fixes += _fixes_for_move_after_select_clause(
                                to_delete[-1], to_delete
                            )
                    elif select_stmt.segments[after_select_clause_idx].is_type(
                        "whitespace"
                    ):
                        # The select_clause has stuff after (most likely a comment)
                        # Delete the whitespace immediately after the select clause
                        # so the other stuff aligns nicely based on where the select
                        # clause started.
                        fixes += [
                            LintFix.delete(
                                select_stmt.segments[after_select_clause_idx],
                            ),
                        ]
                        fixes += _fixes_for_move_after_select_clause(
                            select_children[
                                select_targets_info.first_select_target_idx
                            ],
                        )
                    elif select_stmt.segments[after_select_clause_idx].is_type(
                        "dedent"
                    ):
                        # Again let's strip back the whitespace, but simpler
                        # as don't need to worry about new line so just break
                        # if see non-whitespace
                        to_delete = select_children.reversed().select(
                            loop_while=sp.is_type("whitespace"),
                            start_seg=select_children[select_clause_idx - 1],
                        )
                        if to_delete:
                            fixes += _fixes_for_move_after_select_clause(
                                to_delete[-1],
                                to_delete,
                                # If we deleted a newline, create a newline.
                                any(seg for seg in to_delete if seg.is_type("newline")),
                            )
                    else:
                        fixes += _fixes_for_move_after_select_clause(
                            select_children[
                                select_targets_info.first_select_target_idx
                            ],
                        )

            if select_targets_info.comment_after_select_idx == -1:
                fixes += [
                    # Insert the select_clause in place of the first newline in the
                    # Select statement
                    LintFix.replace(
                        select_children[select_targets_info.first_new_line_idx],
                        insert_buff,
                    ),
                ]
            else:
                # The SELECT is followed by a comment on the same line. In order
                # to autofix this, we'd need to move the select target between
                # SELECT and the comment and potentially delete the entire line
                # where the select target was (if it is now empty). This is
                # *fairly tricky and complex*, in part because the newline on
                # the select target's line is several levels higher in the
                # parser tree. Hence, we currently don't autofix this. Could be
                # autofixed in the future if/when we have the time.
                fixes = []
            return LintResult(
                anchor=select_clause.get(),
                fixes=fixes,
            )
        return None
