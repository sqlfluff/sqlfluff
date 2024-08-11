"""Implementation of Rule LT09."""

from typing import List, NamedTuple, Optional, Sequence

from sqlfluff.core.parser import BaseSegment, NewlineSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, Segments, sp


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


class Rule_LT09(BaseRule):
    """Select targets should be on a new line unless there is only one select target.

    .. note::
       By default, a wildcard (e.g. ``SELECT *``) is considered a single select target.
       If you want it to be treated as multiple select targets, configure
       ``wildcard_policy = multiple``.

    **Anti-pattern**

    Multiple select targets on the same line.

    .. code-block:: sql

        select a, b
        from foo;

        -- Single select target on its own line.

        SELECT
            a
        FROM foo;


    **Best practice**

    Multiple select targets each on their own line.

    .. code-block:: sql

        select
            a,
            b
        from foo;

        -- Single select target on the same line as the ``SELECT``
        -- keyword.

        SELECT a
        FROM foo;

        -- When select targets span multiple lines, however they
        -- can still be on a new line.

        SELECT
            SUM(
                1 + SUM(
                    2 + 3
                )
            ) AS col
        FROM test_table;

    """

    name = "layout.select_targets"
    aliases = ("L036",)
    groups = ("all", "layout")
    config_keywords = ["wildcard_policy"]
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
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
        return None

    @staticmethod
    def _get_indexes(context: RuleContext) -> SelectTargetsInfo:
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

    def _eval_multiple_select_target_elements(
        self, select_targets_info, segment
    ) -> Optional[LintResult]:
        """Multiple select targets. Ensure each is on a separate line."""
        fixes = []
        previous_code = None
        select_clause_raws = Segments(segment).raw_segments
        for i, select_target in enumerate(select_targets_info.select_targets):
            assert select_target.pos_marker
            target_start_line = select_target.pos_marker.working_line_no
            target_initial_code = (
                Segments(select_target).raw_segments.first(sp.is_code()).get()
            )
            assert target_initial_code
            previous_code = (
                select_clause_raws.select(
                    # Get the first code that isn't a comma.
                    select_if=sp.and_(sp.is_code(), sp.not_(sp.raw_is(","))),
                    start_seg=previous_code,
                    stop_seg=target_initial_code,
                )
                .last()
                .get()
            )
            assert previous_code
            assert previous_code.pos_marker
            previous_end_line = previous_code.pos_marker.working_line_no
            self.logger.debug(
                "- Evaluating %s [%s, %s]: Prev ends with: %s",
                select_target,
                previous_end_line,
                target_start_line,
                previous_code,
            )

            # Check whether this target *starts* on the same line that the
            # previous one *ends* on. If they are on the same line, insert a newline.
            if target_start_line == previous_end_line:
                # Find and delete any whitespace before the select target.
                start_seg = select_targets_info.select_idx
                # If any select modifier (e.g. distinct ) is present, start
                # there rather than at the beginning.
                modifier = segment.get_child("select_clause_modifier")
                if modifier:
                    start_seg = segment.segments.index(modifier)

                ws_to_delete = segment.select_children(
                    start_seg=(
                        segment.segments[start_seg]
                        if not i
                        else select_targets_info.select_targets[i - 1]
                    ),
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

        return None

    def _eval_single_select_target_element(
        self, select_targets_info, context: RuleContext
    ):
        select_clause = FunctionalContext(context).segment
        parent_stack = context.parent_stack
        target_idx = select_targets_info.first_select_target_idx
        select_children = select_clause.children()
        target_seg = select_children[target_idx]

        # If it's all on one line, then there's no issue.
        if not (
            select_targets_info.select_idx
            < select_targets_info.first_new_line_idx
            < target_idx
        ):
            self.logger.info(
                "Target at index %s is already on a single line.",
                target_idx,
            )
            return None

        # Does the target contain a newline?
        # i.e. even if it's a single element, does it already span more than
        # one line?
        if "newline" in target_seg.descendant_type_set:
            self.logger.info(
                "Target at index %s spans multiple lines so ignoring.",
                target_idx,
            )
            return None

        if select_targets_info.comment_after_select_idx != -1:
            # The SELECT is followed by a comment on the same line. In order
            # to autofix this, we'd need to move the select target between
            # SELECT and the comment and potentially delete the entire line
            # where the select target was (if it is now empty). This is
            # *fairly tricky and complex*, in part because the newline on
            # the select target's line is several levels higher in the
            # parser tree. Hence, we currently don't autofix this. Could be
            # autofixed in the future if/when we have the time.
            return LintResult(anchor=select_clause.get())

        # Prepare the select clause which will be inserted
        insert_buff = [WhitespaceSegment(), target_seg]
        # Delete the first select target from its original location.
        # We'll add it to the right section at the end, once we know
        # what to add.
        initial_deletes = [target_seg]
        # If there's whitespace before it, delete that too.
        if select_children[target_idx - 1].is_type("whitespace"):
            initial_deletes.append(select_children[target_idx - 1])

        # Do we have a modifier?
        modifier: Optional[Segments]
        modifier = select_children.first(sp.is_type("select_clause_modifier"))

        if (
            # Check if the modifier is one we care about
            modifier
            # We only care if it's not already on the first line.
            and select_children.index(modifier.get())
            >= select_targets_info.first_new_line_idx
        ):
            # Prepend it to the insert buffer
            insert_buff = [WhitespaceSegment(), modifier[0]] + insert_buff

            modifier_idx = select_children.index(modifier.get())
            # Delete the whitespace after it (which is two after, thanks to indent)
            if (
                len(select_children) > modifier_idx + 1
                and select_children[modifier_idx + 2].is_whitespace
            ):
                initial_deletes.append(select_children[modifier_idx + 2])

            # Delete the modifier itself
            initial_deletes.append(modifier[0])

            # Set the position marker for removing the preceding
            # whitespace and newline, which we'll use below.
            start_idx = modifier_idx
            start_seg = modifier[0]
        else:
            # Set the position marker for removing the preceding
            # whitespace and newline, which we'll use below.
            start_idx = target_idx
            start_seg = select_children[select_targets_info.first_new_line_idx]

        fixes = [
            # Insert the select_clause in place of the first newline in the
            # Select statement
            LintFix.replace(
                select_children[select_targets_info.first_new_line_idx],
                insert_buff,
            ),
            # Materialise any deletes so far...
            *(LintFix.delete(seg) for seg in initial_deletes),
        ]

        if parent_stack and parent_stack[-1].is_type("select_statement"):
            select_stmt = parent_stack[-1]
            select_clause_idx = select_stmt.segments.index(select_clause.get())
            after_select_clause_idx = select_clause_idx + 1

            if len(select_stmt.segments) > after_select_clause_idx:
                add_newline = True
                to_delete: Sequence[BaseSegment] = [target_seg]
                next_segment = select_stmt.segments[after_select_clause_idx]

                if next_segment.is_type("newline"):
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
                            fixes.append(LintFix.delete(next_segment))

                elif next_segment.is_type("whitespace"):
                    # The select_clause has stuff after (most likely a comment)
                    # Delete the whitespace immediately after the select clause
                    # so the other stuff aligns nicely based on where the select
                    # clause started.
                    fixes.append(LintFix.delete(next_segment))

                if to_delete:
                    # Clean up by moving leftover select_clause segments.

                    # Context: Some of the other fixes we make in
                    # _eval_single_select_target_element() leave leftover
                    # child segments that need to be moved to become
                    # *siblings* of the select_clause.
                    move_after_select_clause = select_children.select(
                        start_seg=start_seg,
                        stop_seg=to_delete[-1],
                    )
                    # :TRICKY: Below, we have a couple places where we
                    # filter to guard against deleting the same segment
                    # multiple times -- this is illegal.
                    all_deletes = set(
                        fix.anchor for fix in fixes if fix.edit_type == "delete"
                    )
                    for seg in (*to_delete, *move_after_select_clause):
                        if seg not in all_deletes:
                            fixes.append(LintFix.delete(seg))
                            all_deletes.add(seg)

                    if move_after_select_clause or add_newline:
                        fixes.append(
                            LintFix.create_after(
                                select_clause[0],
                                ([NewlineSegment()] if add_newline else [])
                                + list(move_after_select_clause),
                            )
                        )

        return LintResult(
            anchor=select_clause.get(),
            fixes=fixes,
        )
