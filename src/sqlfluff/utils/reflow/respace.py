"""Static methods to support ReflowPoint.respace_point()."""

import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, cast

from sqlfluff.core.errors import SQLFluffUserError
from sqlfluff.core.parser import (
    BaseSegment,
    PositionMarker,
    RawSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import LintFix, LintResult
from sqlfluff.utils.reflow.helpers import pretty_segment_name

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.utils.reflow.elements import ReflowBlock


# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


def _unpack_constraint(constraint: str, strip_newlines: bool) -> Tuple[str, bool]:
    """Unpack a spacing constraint.

    Used as a helper function in `determine_constraints`.
    """
    # Check for deprecated options.
    if constraint == "inline":  # pragma: no cover
        reflow_logger.warning(
            "Found 'inline' specified as a 'spacing_within' constraint. "
            "This setting is deprecated and has been replaced by the more "
            "explicit 'touch:inline'. Upgrade your configuration to "
            "remove this warning."
        )
        constraint = "touch:inline"

    # Unless align, split.
    if constraint.startswith("align"):
        modifier = ""
    else:
        constraint, _, modifier = constraint.partition(":")

    if not modifier:
        pass
    elif modifier == "inline":
        strip_newlines = True
    else:  # pragma: no cover
        raise SQLFluffUserError(f"Unexpected constraint modifier: {constraint!r}")

    return constraint, strip_newlines


def determine_constraints(
    prev_block: Optional["ReflowBlock"],
    next_block: Optional["ReflowBlock"],
    strip_newlines: bool = False,
) -> Tuple[str, str, bool]:
    """Given the surrounding blocks, determine appropriate constraints."""
    # Start with the defaults.
    pre_constraint, strip_newlines = _unpack_constraint(
        prev_block.spacing_after if prev_block else "single", strip_newlines
    )
    post_constraint, strip_newlines = _unpack_constraint(
        next_block.spacing_before if next_block else "single", strip_newlines
    )

    # Work out the common parent segment and depth
    within_spacing = ""
    if prev_block and next_block:
        common = prev_block.depth_info.common_with(next_block.depth_info)
        # Just check the most immediate parent for now for speed.
        # TODO: Review whether just checking the parent is enough.
        # NOTE: spacing configs will be available on both sides if they're common
        # so it doesn't matter whether we get it from prev_block or next_block.
        idx = prev_block.depth_info.stack_hashes.index(common[-1])

        within_constraint = prev_block.stack_spacing_configs.get(common[-1], None)
        if within_constraint:
            within_spacing, strip_newlines = _unpack_constraint(
                within_constraint, strip_newlines
            )

    # If segments are expected to be touch within. Then modify
    # constraints accordingly.
    if within_spacing == "touch":
        # NOTE: We don't override if it's already "any"
        if pre_constraint != "any":
            pre_constraint = "touch"
        if post_constraint != "any":
            post_constraint = "touch"
    elif within_spacing == "any":
        pre_constraint = "any"
        post_constraint = "any"
    elif within_spacing == "single":
        pass
    elif within_spacing:  # pragma: no cover
        assert prev_block
        raise SQLFluffUserError(
            f"Unexpected within constraint: {within_constraint!r} for "
            f"{prev_block.depth_info.stack_class_types[idx]}"
        )

    return pre_constraint, post_constraint, strip_newlines


def process_spacing(
    segment_buffer: List[RawSegment], strip_newlines: bool = False
) -> Tuple[List[RawSegment], Optional[RawSegment], List[LintResult]]:
    """Given the existing spacing, extract information and do basic pruning."""
    removal_buffer: List[RawSegment] = []
    result_buffer: List[LintResult] = []
    last_whitespace: List[RawSegment] = []

    # Loop through the existing segments looking for spacing.
    for seg in segment_buffer:
        # If it's whitespace, store it.
        if seg.is_type("whitespace"):
            last_whitespace.append(seg)

        # If it's a newline, react accordingly.
        # NOTE: This should only trigger on literal newlines.
        elif seg.is_type("newline", "end_of_file"):
            if seg.pos_marker and not seg.pos_marker.is_literal():
                last_whitespace = []
                reflow_logger.debug("    Skipping templated newline: %s", seg)
                continue

            # Are we stripping newlines?
            if strip_newlines and seg.is_type("newline"):
                reflow_logger.debug("    Stripping newline: %s", seg)
                removal_buffer.append(seg)
                result_buffer.append(
                    LintResult(
                        seg, [LintFix.delete(seg)], description="Unexpected line break."
                    )
                )
                # Carry on as though it wasn't here.
                continue

            # Check if we've just passed whitespace. If we have, remove it
            # as trailing whitespace, both from the buffer and create a fix.
            if last_whitespace:
                reflow_logger.debug("    Removing trailing whitespace.")
                for ws in last_whitespace:
                    removal_buffer.append(ws)
                    result_buffer.append(
                        LintResult(
                            ws,
                            [LintFix.delete(ws)],
                            description="Unnecessary trailing whitespace.",
                        )
                    )

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
            result_buffer.append(
                LintResult(
                    seg,
                    [LintFix.delete(seg)],
                    description="Removing duplicate whitespace.",
                )
            )

    # Turn the removal buffer updated segment buffer, last whitespace
    # and associated fixes.
    return (
        [s for s in segment_buffer if s not in removal_buffer],
        # We should have removed all other whitespace by now.
        last_whitespace[0] if last_whitespace else None,
        result_buffer,
    )


def _determine_aligned_inline_spacing(
    root_segment: BaseSegment,
    whitespace_seg: RawSegment,
    next_seg: RawSegment,
    next_pos: PositionMarker,
    segment_type: str,
    align_within: Optional[str],
    align_scope: Optional[str],
) -> str:
    """Work out spacing for instance of an `align` constraint."""
    # Find the level of segment that we're aligning.
    # NOTE: Reverse slice
    parent_segment = None

    # Edge case: if next_seg has no position, we should use the position
    # of the whitespace for searching.
    if align_within:
        for ps in root_segment.path_to(
            next_seg if next_seg.pos_marker else whitespace_seg
        )[::-1]:
            if ps.segment.is_type(align_within):
                parent_segment = ps.segment
            if align_scope and ps.segment.is_type(align_scope):
                break

    if not parent_segment:
        reflow_logger.debug("    No Parent found for alignment case. Treat as single.")
        return " "

    # We've got a parent. Find some siblings.
    reflow_logger.debug("    Determining alignment within: %s", parent_segment)
    siblings = []
    for sibling in parent_segment.recursive_crawl(segment_type):
        # Purge any siblings with a boundary between them
        if not align_scope or not any(
            ps.segment.is_type(align_scope) for ps in parent_segment.path_to(sibling)
        ):
            siblings.append(sibling)
        else:
            reflow_logger.debug(
                "    Purging a sibling because they're blocked " "by a boundary: %s",
                sibling,
            )

    # If the segment we're aligning, has position. Use that position.
    # If it doesn't, then use the provided one. We can't do sibling analysis without it.
    if next_seg.pos_marker:
        next_pos = next_seg.pos_marker

    # Purge any siblings which are either self, or on the same line but after it.
    _earliest_siblings: Dict[int, int] = {}
    for sibling in siblings[:]:
        _pos = sibling.pos_marker
        assert _pos
        _best_seen = _earliest_siblings.get(_pos.working_line_no, None)
        # If we've already seen an earlier sibling on this line, ignore the later one.
        if _best_seen is not None and _pos.working_line_pos > _best_seen:
            siblings.remove(sibling)
            continue
        # Update best seen
        _earliest_siblings[_pos.working_line_no] = _pos.working_line_pos

        # We should also purge the sibling which matches the target.
        if _pos.working_line_no == next_pos.working_line_no:
            # Is it in the same position?
            if _pos.working_line_pos != next_pos.working_line_pos:
                siblings.remove(sibling)

    # If there's only one sibling, we have nothing to compare to. Default to a single
    # space.
    if len(siblings) <= 1:
        desired_space = " "
        reflow_logger.debug(
            "    desired_space: %r (based on no other siblings)",
            desired_space,
        )
        return desired_space

    # Work out the current spacing before each.
    last_code = None
    max_desired_line_pos = 0
    for seg in parent_segment.raw_segments:
        for sibling in siblings:
            # NOTE: We're asserting that there must have been
            # a last_code. Otherwise this won't work.
            if (
                seg.pos_marker
                and sibling.pos_marker
                and seg.pos_marker.working_loc == sibling.pos_marker.working_loc
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


def _extract_alignment_config(
    constraint: str,
) -> Tuple[str, Optional[str], Optional[str]]:
    """Helper function to break apart an alignment config.

    >>> _extract_alignment_config("align:alias_expression")
    ('alias_expression', None, None)
    >>> _extract_alignment_config("align:alias_expression:statement")
    ('alias_expression', 'statement', None)
    >>> _extract_alignment_config("align:alias_expression:statement:bracketed")
    ('alias_expression', 'statement', 'bracketed')
    """
    assert ":" in constraint
    alignment_config = constraint.split(":")
    assert alignment_config[0] == "align"
    seg_type = alignment_config[1]
    align_within = alignment_config[2] if len(alignment_config) > 2 else None
    align_scope = alignment_config[3] if len(alignment_config) > 3 else None
    reflow_logger.debug(
        "    Alignment Config: %s, %s, %s",
        seg_type,
        align_within,
        align_scope,
    )
    return seg_type, align_within, align_scope


def handle_respace__inline_with_space(
    pre_constraint: str,
    post_constraint: str,
    prev_block: Optional["ReflowBlock"],
    next_block: Optional["ReflowBlock"],
    root_segment: BaseSegment,
    segment_buffer: List[RawSegment],
    last_whitespace: RawSegment,
) -> Tuple[List[RawSegment], List[LintResult]]:
    """Check inline spacing is the right size.

    This forms one of the cases handled by .respace_point().

    This code assumes:
    - a ReflowPoint with no newlines.
    - a ReflowPoint which has _some_ whitespace.

    Given this we apply constraints to ensure the whitespace
    is of an appropriate size.
    """
    # Get some indices so that we can reference around them
    ws_idx = segment_buffer.index(last_whitespace)

    # Do we have either side set to "any"
    if "any" in [pre_constraint, post_constraint]:
        # In this instance - don't change anything.
        # e.g. this could mean there is a comment on one side.
        return segment_buffer, []

    # Do we have either side set to "touch"?
    if "touch" in [pre_constraint, post_constraint]:
        # In this instance - no whitespace is correct, This
        # means we should delete it.
        segment_buffer.pop(ws_idx)
        if next_block:
            description = (
                "Unexpected whitespace before "
                f"{pretty_segment_name(next_block.segments[0])}."
            )
        else:  # pragma: no cover
            # This clause has no test coverage because next_block is
            # normally provided.
            description = "Unexpected whitespace"

        return segment_buffer, [
            LintResult(
                last_whitespace,
                [LintFix.delete(last_whitespace)],
                # Should make description from constraints.
                description=description,
            ),
        ]

    # Handle left alignment & singles
    if (
        post_constraint.startswith("align") and next_block
    ) or pre_constraint == post_constraint == "single":
        # Determine the desired spacing, either as alignment or as a single.
        if post_constraint.startswith("align") and next_block:
            seg_type, align_within, align_scope = _extract_alignment_config(
                post_constraint
            )

            next_pos: Optional[PositionMarker]
            if next_block.segments[0].pos_marker:
                next_pos = next_block.segments[0].pos_marker
            elif last_whitespace.pos_marker:
                next_pos = last_whitespace.pos_marker.end_point_marker()
            # These second clauses are much less likely and so are excluded from
            # coverage. If we find a way of covering them, that would be great
            # but for now they exist as backups.
            elif prev_block and prev_block.segments[-1].pos_marker:  # pragma: no cover
                next_pos = prev_block.segments[-1].pos_marker.end_point_marker()
            else:  # pragma: no cover
                reflow_logger.info("Unable to find position marker for alignment.")
                next_pos = None
                desired_space = " "
                desc = (
                    "Expected only single space. " "Found " f"{last_whitespace.raw!r}."
                )

            if next_pos:
                desired_space = _determine_aligned_inline_spacing(
                    root_segment,
                    last_whitespace,
                    next_block.segments[0],
                    next_pos,
                    seg_type,
                    align_within,
                    align_scope,
                )

                desc = (
                    f"{seg_type!r} elements are expected to be aligned. Found "
                    "incorrect whitespace before "
                    f"{pretty_segment_name(next_block.segments[0])}: "
                    f"{last_whitespace.raw!r}."
                )
        else:
            if next_block:
                desc = (
                    "Expected only single space before "
                    f"{pretty_segment_name(next_block.segments[0])}. Found "
                    f"{last_whitespace.raw!r}."
                )
            else:  # pragma: no cover
                # This clause isn't has no test coverage because next_block is
                # normally provided.
                desc = "Expected only single space. Found " f"{last_whitespace.raw!r}."
            desired_space = " "

        new_results: List[LintResult] = []

        if last_whitespace.raw != desired_space:
            new_seg = last_whitespace.edit(desired_space)
            new_results.append(
                LintResult(
                    last_whitespace,
                    [
                        LintFix(
                            "replace",
                            anchor=last_whitespace,
                            edit=[new_seg],
                        )
                    ],
                    description=desc,
                )
            )
            segment_buffer[ws_idx] = new_seg

        return segment_buffer, new_results

    raise NotImplementedError(  # pragma: no cover
        f"Unexpected Constraints: {pre_constraint}, {post_constraint}"
    )


def handle_respace__inline_without_space(
    pre_constraint: str,
    post_constraint: str,
    prev_block: Optional["ReflowBlock"],
    next_block: Optional["ReflowBlock"],
    segment_buffer: List[RawSegment],
    existing_results: List[LintResult],
    anchor_on: str = "before",
) -> Tuple[List[RawSegment], List[LintResult], bool]:
    """Ensure spacing is the right size.

    This forms one of the cases handled by .respace_point().

    This code assumes:
    - a ReflowPoint with no newlines.
    - a ReflowPoint which _no_ whitespace.

    Given this we apply constraints to either confirm no
    spacing is required or create some of the right size.
    """
    # Do we have either side set to "touch" or "any"
    if {"touch", "any"}.intersection([pre_constraint, post_constraint]):
        # In this instance - no whitespace is correct.
        # Either because there shouldn't be, or because "any"
        # means we shouldn't check.
        return segment_buffer, existing_results, False
    # Are we supposed to be aligning?
    elif post_constraint.startswith("align"):
        reflow_logger.debug("    Inserting Aligned Whitespace.")
        # TODO: We currently rely on a second pass to align
        # insertions. This is where we could devise alignment
        # in advance, but most of the alignment code relies on
        # having existing position markers for those insertions.
        # https://github.com/sqlfluff/sqlfluff/issues/4492
        desired_space = " "
        added_whitespace = WhitespaceSegment(desired_space)
    # Is it anything other than the default case?
    elif not (pre_constraint == post_constraint == "single"):  # pragma: no cover
        # TODO: This will get test coverage when configuration routines
        # are in properly.
        raise NotImplementedError(
            f"Unexpected Constraints: {pre_constraint}, {post_constraint}"
        )
    else:
        # Default to a single whitespace
        reflow_logger.debug("    Inserting Single Whitespace.")
        added_whitespace = WhitespaceSegment()

    # Add it to the buffer first (the easy bit). The hard bit
    # is to then determine how to generate the appropriate LintFix
    # objects.
    segment_buffer.append(added_whitespace)

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
        if not existing_results:  # pragma: no cover
            raise ValueError(
                "Fixes detected, but none passed to .respace(). "
                "This will cause conflicts."
            )
        # Find the fix
        assert insertion
        for res in existing_results:
            # Does it contain the insertion?
            # TODO: This feels ugly - eq for BaseSegment is different
            # to uuid matching for RawSegment. Perhaps this should be
            # more aligned. There might be a better way of doing this.
            for fix in res.fixes or []:
                if fix.edit and insertion.uuid in [elem.uuid for elem in fix.edit]:
                    break
            else:  # pragma: no cover
                continue
            break
        else:  # pragma: no cover
            reflow_logger.warning("Results %s", existing_results)
            raise ValueError(f"Couldn't find insertion for {insertion}")
        # Mutate the existing fix
        assert res
        assert fix
        assert fix in res.fixes
        assert fix.edit  # It's going to be an edit if we've picked it up.
        # Mutate the fix, it's still in the same result, and that result
        # is still in the existing_results.
        if existing_fix == "before":
            fix.edit = [cast(BaseSegment, added_whitespace)] + fix.edit
        elif existing_fix == "after":
            fix.edit = fix.edit + [cast(BaseSegment, added_whitespace)]

        # No need to add new results, because we mutated the existing.
        return segment_buffer, existing_results, True

    # Otherwise...
    reflow_logger.debug("    Not Detected existing fix. Creating new")
    if prev_block and next_block:
        desc = (
            "Expected single whitespace between "
            f"{pretty_segment_name(prev_block.segments[-1])} "
            f"and {pretty_segment_name(next_block.segments[0])}."
        )
    else:  # pragma: no cover
        # Something to fall back on if prev_block and next_block not provided.
        desc = "Expected single whitespace."
    # Take into account hint on where to anchor if given.
    if prev_block and anchor_on != "after":
        new_result = LintResult(
            # We do this shuffle, because for the CLI it's clearer if the
            # anchor for the error is at the point that the insertion will
            # happen which is the *start* of the next segment, even if
            # we're anchoring the fix on the previous.
            next_block.segments[0] if next_block else prev_block.segments[-1],
            fixes=[
                LintFix(
                    "create_after",
                    anchor=prev_block.segments[-1],
                    edit=[WhitespaceSegment()],
                )
            ],
            description=desc,
        )
    elif next_block:
        new_result = LintResult(
            next_block.segments[0],
            fixes=[
                LintFix(
                    "create_before",
                    anchor=next_block.segments[0],
                    edit=[WhitespaceSegment()],
                )
            ],
            description=desc,
        )
    else:  # pragma: no cover
        NotImplementedError("Not set up to handle a missing _after_ and _before_.")

    return segment_buffer, existing_results + [new_result], True
