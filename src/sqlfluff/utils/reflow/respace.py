"""Static methods to support ReflowPoint.respace_point()."""


import logging
from typing import List, Optional, Tuple, cast, TYPE_CHECKING

from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.parser.segments.raw import WhitespaceSegment
from sqlfluff.core.rules.base import LintFix


if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.utils.reflow.elements import ReflowBlock


# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


def determine_constraints(
    prev_block: Optional["ReflowBlock"],
    next_block: Optional["ReflowBlock"],
    strip_newlines: bool = False,
) -> Tuple[str, str, bool]:
    """Given the surrounding blocks, determine appropriate constraints."""
    # Start with the defaults.
    pre_constraint = prev_block.spacing_after if prev_block else "single"
    post_constraint = next_block.spacing_before if next_block else "single"

    # Work out the common parent segment and depth
    if prev_block and next_block:
        common = prev_block.depth_info.common_with(next_block.depth_info)
        # Just check the most immediate parent for now for speed.
        # TODO: Review whether just checking the parent is enough.
        # NOTE: spacing configs will be available on both sides if they're common
        # so it doesn't matter whether we get it from prev_block or next_block.
        within_constraint = prev_block.stack_spacing_configs.get(common[-1], None)
        if not within_constraint:
            pass
        elif within_constraint in ("touch", "inline"):
            # NOTE: inline is actually a more extreme version of "touch".
            # Examples:
            # - "inline" would be used with an object reference, where the
            #   parts have to all be together on one line like `a.b.c`.
            # - "touch" would allow the above layout, _but also_ allow an
            #   an optional line break between, much like between an opening
            #   bracket and the following element: `(a)` or:
            #   ```
            #   (
            #       a
            #   )
            #   ```
            if within_constraint == "inline":
                # If they are then strip newlines.
                strip_newlines = True
            # If segments are expected to be touch within. Then modify
            # constraints accordingly.
            # NOTE: We don't override if it's already "any"
            if pre_constraint != "any":
                pre_constraint = "touch"
            if post_constraint != "any":
                post_constraint = "touch"
        else:  # pragma: no cover
            idx = prev_block.depth_info.stack_hashes.index(common[-1])
            raise NotImplementedError(
                f"Unexpected within constraint: {within_constraint} for "
                f"{prev_block.depth_info.stack_class_types[idx]}"
            )

    return pre_constraint, post_constraint, strip_newlines


def process_spacing(
    segment_buffer: List[RawSegment], strip_newlines: bool = False
) -> Tuple[List[RawSegment], Optional[RawSegment], List[LintFix]]:
    """Given the existing spacing, extract information and do basic pruning."""
    removal_buffer: List[RawSegment] = []
    last_whitespace: List[RawSegment] = []

    # Loop through the existing segments looking for spacing.
    for seg in segment_buffer:

        # If it's whitespace, store it.
        if seg.is_type("whitespace"):
            last_whitespace.append(seg)

        # If it's a newline, react accordingly.
        elif seg.is_type("newline", "end_of_file"):

            # Are we stripping newlines?
            if strip_newlines and seg.is_type("newline"):
                reflow_logger.debug("    Stripping newline: %s", seg)
                removal_buffer.append(seg)
                # Carry on as though it wasn't here.
                continue

            # Check if we've just passed whitespace. If we have, remove it
            # as trailing whitespace, both from the buffer and create a fix.
            if last_whitespace:
                reflow_logger.debug("    Removing trailing whitespace.")
                for ws in last_whitespace:
                    removal_buffer.append(ws)

            # Regardless, unset last_whitespace.
            # We either just deleted it, or it's not relevant for any future
            # segments.
            last_whitespace = []

    if len(last_whitespace) >= 2:
        reflow_logger.debug("   Removing adjoining whitespace.")
        # If we find multiple sequential whitespaces, it's the sign
        # that we've removed something. Only the first one should be
        # a valid indent (or the one we consider for constraints).
        # Remove all the following ones.
        for ws in last_whitespace[1:]:
            removal_buffer.append(ws)

    # Turn the removal buffer updated segment buffer, last whitespace
    # and associated fixes.
    return (
        [s for s in segment_buffer if s not in removal_buffer],
        # We should have removed all other whitespace by now.
        last_whitespace[0] if last_whitespace else None,
        [LintFix.delete(s) for s in removal_buffer],
    )


def _determine_aligned_inline_spacing(
    root_segment: BaseSegment,
    whitespace_seg: RawSegment,
    next_seg: RawSegment,
    segment_type: str,
    align_within: Optional[str],
    align_scope: Optional[str],
) -> str:
    """Work out spacing for instance of an `align` constraint."""
    # Find the level of segment that we're aligning.
    # NOTE: Reverse slice
    parent_segment = None
    for ps in root_segment.path_to(next_seg)[::-1]:
        if ps.segment.is_type(align_within):
            parent_segment = ps.segment
        if ps.segment.is_type(align_scope):
            break

    if not parent_segment:
        reflow_logger.debug("    No Parent found for alignment case. Treat as single.")
        return " "

    # We've got a parent. Find some siblings.
    reflow_logger.debug("    Determining alignment within: %s", parent_segment)
    siblings = []
    for sibling in parent_segment.recursive_crawl(segment_type):
        # Purge any siblings with a boundary between them
        if not any(
            ps.segment.is_type(align_scope) for ps in parent_segment.path_to(sibling)
        ):
            siblings.append(sibling)
        else:
            reflow_logger.debug(
                "    Purging a sibling because they're blocked " "by a boundary: %s",
                sibling,
            )

    # Is the current indent the only one on the line?
    if any(
        # Same line
        sibling.pos_marker.working_line_no == next_seg.pos_marker.working_line_no
        # And not same position (i.e. not self)
        and sibling.pos_marker.working_line_pos != next_seg.pos_marker.working_line_pos
        for sibling in siblings
    ):
        reflow_logger.debug("    Found sibling on same line. Treat as single")
        return " "

    # Work out the current spacing before each.
    last_code = None
    max_desired_line_pos = 0
    for seg in parent_segment.raw_segments:
        for sibling in siblings:
            # NOTE: We're asserting that there must have been
            # a last_code. Otherwise this won't work.
            if (
                seg.pos_marker.working_loc == sibling.pos_marker.working_loc
                and last_code
            ):
                loc = last_code.pos_marker.working_loc_after(last_code.raw)
                reflow_logger.debug(
                    "    loc for %s: %s from %s",
                    sibling,
                    loc,
                    last_code,
                )
                if loc[1] > max_desired_line_pos:
                    max_desired_line_pos = loc[1]
        if seg.is_code:
            last_code = seg

    desired_space = " " * (
        1 + max_desired_line_pos - whitespace_seg.pos_marker.working_line_pos
    )
    reflow_logger.debug(
        "    desired_space: %r (based on max line pos of %s)",
        desired_space,
        max_desired_line_pos,
    )
    return desired_space


def handle_respace__inline_with_space(
    pre_constraint: str,
    post_constraint: str,
    next_block: Optional["ReflowBlock"],
    root_segment: BaseSegment,
    segment_buffer: List[RawSegment],
    last_whitespace: RawSegment,
) -> Tuple[List[RawSegment], List[LintFix]]:
    """Check inline spacing is the right size.

    This forms one of the cases handled by .respace_point().

    This code assumes:
    - a ReflowPoint with no newlines.
    - a ReflowPoint which has _some_ whitespace.

    Given this we apply constraints to ensure the whitespace
    is of an appropriate size.
    """
    new_fixes: List[LintFix] = []
    # Get some indices so that we can reference around them
    ws_idx = segment_buffer.index(last_whitespace)

    # Do we have either side set to "any"
    if "any" in [pre_constraint, post_constraint]:
        # In this instance - don't change anything.
        # e.g. this could mean there is a comment on one side.
        return segment_buffer, new_fixes

    # Do we have either side set to "touch"?
    if "touch" in [pre_constraint, post_constraint]:
        # In this instance - no whitespace is correct, This
        # means we should delete it.
        new_fixes.append(
            LintFix(
                "delete",
                anchor=last_whitespace,
            )
        )
        segment_buffer.pop(ws_idx)
        return segment_buffer, new_fixes

    # Handle left alignment & singles
    if (
        post_constraint.startswith("align") and next_block
    ) or pre_constraint == post_constraint == "single":

        # Determine the desired spacing, either as alignment or as a single.
        if post_constraint.startswith("align") and next_block:
            alignment_config = post_constraint.split(":")
            seg_type = alignment_config[1]
            align_within = alignment_config[2] if len(alignment_config) > 2 else None
            align_scope = alignment_config[3] if len(alignment_config) > 3 else None
            reflow_logger.debug(
                "    Alignment Config: %s, %s, %s, %s",
                seg_type,
                align_within,
                align_scope,
                next_block.segments[0].pos_marker.working_line_pos,
            )

            desired_space = _determine_aligned_inline_spacing(
                root_segment,
                last_whitespace,
                next_block.segments[0],
                seg_type,
                align_within,
                align_scope,
            )
        else:
            desired_space = " "

        if last_whitespace.raw != desired_space:
            new_seg = last_whitespace.edit(desired_space)
            new_fixes.append(
                LintFix(
                    "replace",
                    anchor=last_whitespace,
                    edit=[new_seg],
                )
            )
            segment_buffer[ws_idx] = new_seg

        return segment_buffer, new_fixes

    raise NotImplementedError(  # pragma: no cover
        f"Unexpected Constraints: {pre_constraint}, {post_constraint}"
    )


def handle_respace__inline_without_space(
    pre_constraint: str,
    post_constraint: str,
    prev_block: Optional["ReflowBlock"],
    next_block: Optional["ReflowBlock"],
    segment_buffer: List[RawSegment],
    existing_fixes: List[LintFix],
    anchor_on: str = "before",
) -> Tuple[List[RawSegment], List[LintFix], bool]:
    """Ensure spacing is the right size.

    This forms one of the cases handled by .respace_point().

    This code assumes:
    - a ReflowPoint with no newlines.
    - a ReflowPoint which _no_ whitespace.

    Given this we apply constraints to either confirm no
    spacing is required or create some of the right size.
    """
    edited = False
    new_fixes: List[LintFix] = []
    # Do we have either side set to "touch" or "any"
    if {"touch", "any"}.intersection([pre_constraint, post_constraint]):
        # In this instance - no whitespace is correct.
        # Either because there shouldn't be, or because "any"
        # means we shouldn't check.
        pass
    # Handle the default case
    elif pre_constraint == post_constraint == "single":
        # Insert a single whitespace.
        reflow_logger.debug("    Inserting Single Whitespace.")
        # Add it to the buffer first (the easy bit). The hard bit
        # is to then determine how to generate the appropriate LintFix
        # objects.
        segment_buffer.append(WhitespaceSegment())
        edited = True

        # So special handling here. If segments either side
        # already exist then we don't care which we anchor on
        # but if one is already an insertion (as shown by a lack)
        # of pos_marker, then we should piggy back on that pre-existing
        # fix.
        existing_fix = None
        insertion = None
        if prev_block and not prev_block.segments[-1].pos_marker:
            existing_fix = "after"
            insertion = prev_block.segments[-1]
        elif next_block and not next_block.segments[0].pos_marker:
            existing_fix = "before"
            insertion = next_block.segments[0]

        if existing_fix:
            reflow_logger.debug("    Detected existing fix %s", existing_fix)
            if not existing_fixes:  # pragma: no cover
                raise ValueError(
                    "Fixes detected, but none passed to .respace(). "
                    "This will cause conflicts."
                )
            # Find the fix
            for fix in existing_fixes:
                # Does it contain the insertion?
                # TODO: This feels ugly - eq for BaseSegment is different
                # to uuid matching for RawSegment. Perhaps this should be
                # more aligned. There might be a better way of doing this.
                if (
                    insertion
                    and fix.edit
                    and insertion.uuid in [elem.uuid for elem in fix.edit]
                ):
                    break
            else:  # pragma: no cover
                reflow_logger.warning("Fixes %s", existing_fixes)
                raise ValueError(f"Couldn't find insertion for {insertion}")
            # Mutate the existing fix
            assert fix
            assert fix.edit  # It's going to be an edit if we've picked it up.
            if existing_fix == "before":
                fix.edit = [cast(BaseSegment, WhitespaceSegment())] + fix.edit
            elif existing_fix == "after":
                fix.edit = fix.edit + [cast(BaseSegment, WhitespaceSegment())]
        else:
            reflow_logger.debug("    Not Detected existing fix. Creating new")
            # Take into account hint on where to anchor if given.
            if prev_block and anchor_on != "after":
                new_fixes.append(
                    LintFix(
                        "create_after",
                        anchor=prev_block.segments[-1],
                        edit=[WhitespaceSegment()],
                    )
                )
            elif next_block:
                new_fixes.append(
                    LintFix(
                        "create_before",
                        anchor=next_block.segments[0],
                        edit=[WhitespaceSegment()],
                    )
                )
            else:  # pragma: no cover
                NotImplementedError(
                    "Not set up to handle a missing _after_ and _before_."
                )
    else:  # pragma: no cover
        # TODO: This will get test coverage when configuration routines
        # are in properly.
        raise NotImplementedError(
            f"Unexpected Constraints: {pre_constraint}, {post_constraint}"
        )

    return segment_buffer, existing_fixes + new_fixes, edited
