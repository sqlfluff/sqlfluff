"""Dataclasses for reflow work."""

from itertools import chain
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple, Type, cast

from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.parser.segments.raw import NewlineSegment, WhitespaceSegment
from sqlfluff.core.rules.base import LintFix

from sqlfluff.utils.reflow.config import ReflowConfig
from sqlfluff.utils.reflow.depthmap import DepthInfo

# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


@dataclass(frozen=True)
class ReflowElement:
    """Base reflow element class."""

    segments: Tuple[RawSegment, ...]

    @staticmethod
    def _class_types(segments: Sequence[RawSegment]) -> Set[str]:
        return set(chain.from_iterable(seg.class_types for seg in segments))

    @property
    def class_types(self):
        """The set of contained class types.

        Parallel to BaseSegment.class_types
        """
        return self._class_types(self.segments)

    @property
    def raw(self):
        """Get the current raw representation."""
        return "".join(seg.raw for seg in self.segments)

    def num_newlines(self) -> int:
        """How many newlines does this element contain?"""
        return sum(
            bool("newline" in seg.class_types) for seg in self.segments
        )


@dataclass(frozen=True)
class ReflowBlock(ReflowElement):
    """Class for keeping track of elements to reflow.

    It holds segments to reflow and also exposes configuration
    around how they are expected to reflow around others.

    The attributes exposed are designed to be "post configuration"
    i.e. they should reflect configuration appropriately.

    NOTE: These are the smallest unit of "work" within
    the reflow methods, and may contain meta segments.
    """

    # Options for spacing rules are:
    # - single:         the default (one single space)
    # - touch:          no whitespace
    # - any:            don't enforce any spacing rules
    spacing_before: str
    spacing_after: str
    # - None:           the default (no particular preference)
    # - leading:        prefer newline before
    # - trailing:       prefer newline after
    line_position: Optional[str]
    # The depth info is used in determining where to put line breaks.
    depth_info: DepthInfo
    # This stores relevant configs for segments in the stack.
    stack_spacing_configs: Dict[int, str]
    line_position_configs: Dict[int, str]

    @classmethod
    def from_config(
        cls: Type["ReflowBlock"], segments, config: ReflowConfig, depth_info: DepthInfo
    ) -> "ReflowBlock":
        """Extendable constructor which accepts config."""
        block_config = config.get_block_config(cls._class_types(segments), depth_info)
        # Populate any spacing_within config.
        # TODO: This needs decent unit tests - not just what happens in rules.
        stack_spacing_configs = {}
        line_position_configs = {}
        for hash, class_types in zip(
            depth_info.stack_hashes, depth_info.stack_class_types
        ):
            cfg = config.get_block_config(class_types)
            if cfg.spacing_within:
                stack_spacing_configs[hash] = cfg.spacing_within
            if cfg.line_position:
                line_position_configs[hash] = cfg.line_position
        return cls(
            segments=segments,
            spacing_before=block_config.spacing_before,
            spacing_after=block_config.spacing_after,
            line_position=block_config.line_position,
            depth_info=depth_info,
            stack_spacing_configs=stack_spacing_configs,
            line_position_configs=line_position_configs,
        )


@dataclass(frozen=True)
class ReflowPoint(ReflowElement):
    """Class for keeping track of editable elements in reflow.

    It holds segments which can be changed during a reflow operation
    such as whitespace and newlines.

    It holds no configuration and is influenced by the blocks either
    side.
    """

    @staticmethod
    def _determine_constraints(
        prev_block: Optional[ReflowBlock],
        next_block: Optional[ReflowBlock],
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

    @staticmethod
    def _process_spacing(
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

    @staticmethod
    def _determine_aligned_inline_spacing(
        root_segment: BaseSegment,
        whitespace_seg: RawSegment,
        next_seg: RawSegment,
        segment_type: str,
        align_within: Optional[str],
        align_boundary: Optional[str],
    ) -> str:
        """Work out spacing for instance of an `align` constraint."""
        # Find the level of segment that we're aligning.
        # NOTE: Reverse slice
        parent_segment = None
        for ps in root_segment.path_to(next_seg)[::-1]:
            if ps.segment.is_type(align_within):
                parent_segment = ps.segment
            if ps.segment.is_type(align_boundary):
                break

        if not parent_segment:
            reflow_logger.debug(
                "    No Parent found for alignment case. Treat as single."
            )
            return " "

        # We've got a parent. Find some siblings.
        reflow_logger.debug("    Determining alignment within: %s", parent_segment)
        siblings = []
        for sibling in parent_segment.recursive_crawl(segment_type):
            # Purge any siblings with a boundary between them
            if not any(
                ps.segment.is_type(align_boundary)
                for ps in parent_segment.path_to(sibling)
            ):
                siblings.append(sibling)
            else:
                reflow_logger.debug(
                    "    Purging a sibling because they're blocked "
                    "by a boundary: %s",
                    sibling,
                )

        # Is the current indent the only one on the line?
        if any(
            # Same line
            sibling.pos_marker.working_line_no == next_seg.pos_marker.working_line_no
            # And not same position (i.e. not self)
            and sibling.pos_marker.working_line_pos
            != next_seg.pos_marker.working_line_pos
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

    @classmethod
    def _handle_respace__inline_with_space(
        cls,
        pre_constraint: str,
        post_constraint: str,
        next_block: Optional[ReflowBlock],
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
                align_within = (
                    alignment_config[2] if len(alignment_config) > 2 else None
                )
                align_boundary = (
                    alignment_config[3] if len(alignment_config) > 3 else None
                )
                reflow_logger.debug(
                    "    Alignment Config: %s, %s, %s, %s",
                    seg_type,
                    align_within,
                    align_boundary,
                    next_block.segments[0].pos_marker.working_line_pos,
                )

                desired_space = cls._determine_aligned_inline_spacing(
                    root_segment,
                    last_whitespace,
                    next_block.segments[0],
                    seg_type,
                    align_within,
                    align_boundary,
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

    @staticmethod
    def _handle_respace__inline_without_space(
        pre_constraint: str,
        post_constraint: str,
        prev_block: Optional[ReflowBlock],
        next_block: Optional[ReflowBlock],
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

    def _get_indent_segment(self) -> Optional[RawSegment]:
        """Get the current indent segment (if there)."""
        indent = None
        for seg in reversed(self.segments):
            if seg.is_type("newline"):
                return indent
            elif seg.is_type("whitespace"):
                indent = seg
        # i.e. if we never find a newline, it's not an indent.
        return None

    def get_indent(self) -> Optional[str]:
        """Get the current indent (if there)."""
        seg = self._get_indent_segment()
        return seg.raw if seg else None

    def indent_to(
        self,
        desired_indent: str,
        after: Optional[BaseSegment] = None,
        before: Optional[BaseSegment] = None,
    ) -> Tuple[List[LintFix], "ReflowPoint"]:
        """Coerce a point to have a particular indent.

        If the point currently contains no newlines, one will
        be introduced and any trailing whitespace will be effectively
        removed.

        More specifically, the newline is _inserted_ before the existing
        whitespace, with the new indent being a replacement for that
        same whitespace.
        """
        # Get the indent (or in the case of no newline, the last whitespace)
        indent_seg = self._get_indent_segment()
        reflow_logger.debug(
            "Coercing indent %s to %r. (newlines: %s)",
            indent_seg,
            desired_indent,
            self.num_newlines(),
        )
        if self.num_newlines():
            # There is already a newline.
            if indent_seg:
                # Coerce existing indent to desired.
                if indent_seg.raw == desired_indent:
                    # Trivial case. Indent already correct
                    return [], self
                elif desired_indent == "":
                    # Coerce to no indent. We don't want the indent. Delete it.
                    new_indent = indent_seg.edit(desired_indent)
                    idx = self.segments.index(indent_seg)
                    return [LintFix.delete(indent_seg)], ReflowPoint(
                        self.segments[:idx] + self.segments[idx + 1 :]
                    )

                # Standard case of an indent change.
                new_indent = indent_seg.edit(desired_indent)
                idx = self.segments.index(indent_seg)
                return [LintFix.replace(indent_seg, [new_indent])], ReflowPoint(
                    self.segments[:idx] + (new_indent,) + self.segments[idx + 1 :]
                )
            else:
                # There is a newline, but no indent. Make one after the newline
                # Find the index of the last newline.
                for idx in range(len(self.segments) - 1, 0, -1):
                    if self.segments[idx].is_type("newline"):
                        break
                new_indent = WhitespaceSegment(desired_indent)
                return [
                    LintFix.create_after(self.segments[idx], [new_indent])
                ], ReflowPoint(
                    self.segments[: idx + 1] + (new_indent,) + self.segments[idx + 1 :]
                )
        else:
            # There isn't currently a newline.
            new_newline = NewlineSegment()
            # Check for whitespace
            ws_seg = None
            for seg in self.segments[::-1]:
                if seg.is_type("whitespace"):
                    ws_seg = seg
            if not ws_seg:
                # There isn't a whitespace segment either. We need to insert one.
                # Do we have an anchor?
                new_indent = WhitespaceSegment(desired_indent)
                if not before and not after:  # pragma: no cover
                    raise NotImplementedError(
                        "Not set up to handle empty points in this "
                        "scenario without provided before/after "
                        f"anchor: {self.segments}"
                    )
                # Otherwise make a new indent, attached to the relevant anchor.
                elif before:
                    fix = LintFix.create_before(before, [new_newline, new_indent])
                else:
                    assert after  # mypy hint
                    fix = LintFix.create_after(after, [new_newline, new_indent])
                new_point = ReflowPoint((new_newline, new_indent))
            else:
                # There is whitespace. Coerce it to the right indent and add
                # a newline _before_. In the edge case that we're coercing to
                # _no indent_, edit existing indent to be the newline and leave
                # it there.
                new_segs: List[RawSegment]
                if desired_indent == "":
                    new_segs = [new_newline]
                else:
                    new_segs = [new_newline, ws_seg.edit(desired_indent)]
                idx = self.segments.index(ws_seg)
                fix = LintFix.replace(ws_seg, new_segs)
                new_point = ReflowPoint(
                    self.segments[:idx] + tuple(new_segs) + self.segments[idx + 1 :]
                )

            return [fix], new_point

    def respace_point(
        self,
        prev_block: Optional[ReflowBlock],
        next_block: Optional[ReflowBlock],
        root_segment: BaseSegment,
        fixes: List[LintFix],
        strip_newlines: bool = False,
        anchor_on: str = "before",
    ) -> Tuple[List[LintFix], "ReflowPoint"]:
        """Respace a point based on given constraints.

        NB: This effectively includes trailing whitespace fixes.

        Deletion and edit fixes are generated immediately, but creations
        are paused to the end and done in bulk so as not to generate conflicts.

        Note that the `strip_newlines` functionality exists here as a slight
        exception to pure respacing, but as a very simple case of positioning
        line breaks. The default operation of `respace` does not enable it
        however it exists as a convenience for rules which wish to use it.
        """
        pre_constraint, post_constraint, strip_newlines = self._determine_constraints(
            prev_block, next_block, strip_newlines
        )

        reflow_logger.debug("Respacing: %s", self)

        # The buffer is used to create the new reflow point to return
        segment_buffer, last_whitespace, new_fixes = self._process_spacing(
            list(self.segments), strip_newlines
        )

        # Check for final trailing whitespace (which otherwise looks like an indent).
        if next_block and "end_of_file" in next_block.class_types and last_whitespace:
            new_fixes.append(LintFix.delete(last_whitespace))
            segment_buffer.remove(last_whitespace)
            last_whitespace = None

        # Is there a newline?
        # NOTE: We do this based on the segment buffer rather than self.class_types
        # because we may have just removed any present newlines in the buffer.
        if (
            any(seg.is_type("newline") for seg in segment_buffer) and not strip_newlines
        ) or (next_block and "end_of_file" in next_block.class_types):
            # Most of this section should be handled as _Indentation_.
            # BUT: There is one case we should handle here.
            # If we find that the last whitespace has a newline
            # before it, and the position markers imply there was
            # a removal between them, then remove the whitespace.
            # This ensures a consistent indent.
            # TODO: Check this doesn't duplicate indentation code
            # once written.

            # The test is less about whether it's longer than one
            # (because we should already have removed additional
            # whitespace above). This is about attempting consistency.
            if last_whitespace:
                ws_idx = self.segments.index(last_whitespace)
                if ws_idx > 0:
                    prev_seg = self.segments[ws_idx - 1]
                    if (
                        prev_seg.is_type("newline")
                        # Not just unequal. Must be actively _before_.
                        # NOTE: Based on working locations
                        and prev_seg.get_end_loc() < last_whitespace.get_start_loc()
                    ):
                        reflow_logger.debug(
                            "    Removing non-contiguous whitespace post removal."
                        )
                        segment_buffer.remove(last_whitespace)
                        new_fixes.append(LintFix("delete", last_whitespace))

        # Is this an inline case? (i.e. no newline)
        else:
            reflow_logger.debug(
                "    Inline case. Constraints: %s <-> %s.",
                pre_constraint,
                post_constraint,
            )

            # Do we at least have _some_ whitespace?
            if last_whitespace:
                # We do - is it the right size?
                segment_buffer, delta_fixes = self._handle_respace__inline_with_space(
                    pre_constraint,
                    post_constraint,
                    next_block,
                    root_segment,
                    segment_buffer,
                    last_whitespace,
                )
                new_fixes.extend(delta_fixes)
            else:
                # No. Should we insert some?
                # NOTE: This method operates on the existing fix buffer.
                (
                    segment_buffer,
                    fixes,
                    edited,
                ) = self._handle_respace__inline_without_space(
                    pre_constraint,
                    post_constraint,
                    prev_block,
                    next_block,
                    segment_buffer,
                    fixes,
                    anchor_on=anchor_on,
                )
                if edited:
                    reflow_logger.debug("    Modified fix buffer: %s", fixes)

        # Only log if we actually made a change.
        if new_fixes:
            reflow_logger.debug("    New Fixes: %s", new_fixes)

        return fixes + new_fixes, ReflowPoint(tuple(segment_buffer))
