"""Dataclasses for reflow work."""

from itertools import chain
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple, Type, Union, cast

from sqlfluff.core.parser.segments import (
    BaseSegment,
    RawSegment,
    NewlineSegment,
    WhitespaceSegment,
    Indent,
)
from sqlfluff.core.rules.base import LintFix

from sqlfluff.utils.reflow.config import ReflowConfig
from sqlfluff.utils.reflow.depthmap import DepthInfo

# Respace Algorithms
from sqlfluff.utils.reflow.respace import (
    determine_constraints,
    process_spacing,
    handle_respace__inline_with_space,
    handle_respace__inline_without_space,
)

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
        return sum(bool("newline" in seg.class_types) for seg in self.segments)


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
        # If no newlines, it's not an indent. Return None.
        if not self.num_newlines():
            return None
        # If there are newlines but no indent segment. Return "".
        seg = self._get_indent_segment()
        return seg.raw if seg else ""

    def get_indent_impulse(self) -> int:
        """Get the change in intended indent balance from this point."""
        return sum(
            cast(Indent, seg).indent_val
            for seg in self.segments
            if seg.is_type("indent")
        )

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
            # There is already a newline. Is there an indent?
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
                # Find the index of the last newline (there _will_ be one because
                # we checked self.num_newlines() above).
                for idx in range(len(self.segments) - 1, -1, -1):
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
        pre_constraint, post_constraint, strip_newlines = determine_constraints(
            prev_block, next_block, strip_newlines
        )

        reflow_logger.debug("Respacing: %s", self)

        # The buffer is used to create the new reflow point to return
        segment_buffer, last_whitespace, new_fixes = process_spacing(
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
                segment_buffer, delta_fixes = handle_respace__inline_with_space(
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
                (segment_buffer, fixes, edited,) = handle_respace__inline_without_space(
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


ReflowSequenceType = List[Union[ReflowBlock, ReflowPoint]]
