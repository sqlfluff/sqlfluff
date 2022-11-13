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
    TemplateSegment,
    Indent,
    SourceFix,
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
    def class_types(self) -> Set[str]:
        """Get the set of contained class types.

        Parallel to `BaseSegment.class_types`
        """
        return self._class_types(self.segments)

    @property
    def raw(self) -> str:
        """Get the current raw representation."""
        return "".join(seg.raw for seg in self.segments)

    def num_newlines(self) -> int:
        """Return the number of newlines in this element."""
        return sum(
            bool(
                "newline" in seg.class_types
                or (
                    "placeholder" in seg.class_types
                    and cast(TemplateSegment, seg).block_type == "literal"
                    and "\n" in cast(TemplateSegment, seg).source_str
                )
            )
            for seg in self.segments
        )


@dataclass(frozen=True)
class ReflowBlock(ReflowElement):
    """Class for keeping track of elements to reflow.

    This class, and its sibling :obj:`ReflowPoint`, should not
    normally be manipulated directly by rules, but instead should
    be manipulated using :obj:`ReflowSequence`.

    It holds segments to reflow and also exposes configuration
    regarding how they are expected to reflow around others. Typically
    it holds only a single element, which is usually code or a
    templated element. Because reflow operations control spacing,
    it would be very unusual for this object to be modified; as
    such it exposes relatively few methods.

    The attributes exposed are designed to be "post configuration"
    i.e. they should reflect configuration appropriately.
    """

    #: Desired spacing before this block.
    #: See :ref:`layoutspacingconfig`
    spacing_before: str
    #: Desired spacing after this block.
    #: See :ref:`layoutspacingconfig`
    spacing_after: str
    #: Desired line position for this block.
    #: See :ref:`layoutspacingconfig`
    line_position: Optional[str]
    #: Metadata on the depth of this segment within the parse tree
    #: which is used in inferring how and where line breaks should
    #: exist.
    depth_info: DepthInfo
    #: Desired spacing configurations for parent segments
    #: of the segment in this block.
    #: See :ref:`layoutspacingconfig`
    stack_spacing_configs: Dict[int, str]
    #: Desired line position configurations for parent segments
    #: of the segment in this block.
    #: See :ref:`layoutspacingconfig`
    line_position_configs: Dict[int, str]

    @classmethod
    def from_config(
        cls: Type["ReflowBlock"], segments, config: ReflowConfig, depth_info: DepthInfo
    ) -> "ReflowBlock":
        """Construct a ReflowBlock while extracting relevant configuration.

        This is the primary route to construct a ReflowBlock, as
        is allows all of the inference of the spacing and position
        configuration from the segments it contains and the
        appropriate config objects.
        """
        block_config = config.get_block_config(cls._class_types(segments), depth_info)
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


def _indent_description(indent: str):
    """Construct a human readable description of the indent."""
    if indent == "":
        return "no indent"
    elif indent[0] == " ":
        assert all(c == " " for c in indent)
        return f"indent of {len(indent)} spaces"
    elif indent[0] == "\t":
        assert all(c == "\t" for c in indent)
        return f"indent of {len(indent)} tabs"
    else:  # pragma: no cover
        raise NotImplementedError(f"Invalid indent construction: {indent!r}")


@dataclass(frozen=True)
class ReflowPoint(ReflowElement):
    """Class for keeping track of editable elements in reflow.

    This class, and its sibling :obj:`ReflowBlock`, should not
    normally be manipulated directly by rules, but instead should
    be manipulated using :obj:`ReflowSequence`.

    It holds segments which can be changed during a reflow operation
    such as whitespace and newlines.It may also contain :obj:`Indent`
    and :obj:`Dedent` elements.

    It holds no configuration and is influenced by the blocks on either
    side, so that any operations on it usually have that configuration
    passed in as required.
    """

    def _get_indent_segment(self) -> Optional[RawSegment]:
        """Get the current indent segment (if there)."""
        indent = None
        for seg in reversed(self.segments):
            if seg.is_type("newline"):
                return indent
            elif seg.is_type("whitespace"):
                indent = seg
            elif (
                seg.is_type("placeholder")
                and "\n" in cast(TemplateSegment, seg).source_str
            ):
                # Consumed whitespace case.
                # NOTE: In this situation, we're not looking for
                # separate newline and indent segments, we're
                # making the assumption that they'll be together
                # which I think is a safe one for now.
                return seg
        # i.e. if we never find a newline, it's not an indent.
        return None

    def get_indent(self) -> Optional[str]:
        """Get the current indent (if there)."""
        # If no newlines, it's not an indent. Return None.
        if not self.num_newlines():
            return None
        # If there are newlines but no indent segment. Return "".
        seg = self._get_indent_segment()
        if seg and seg.is_type("placeholder"):  # pragma: no cover
            # Return last bit after newline.
            # NOTE: Not tested, because usually this would happen
            # directly via _get_indent_segment.
            return cast(TemplateSegment, seg).source_str.split("\n")[-1]
        return seg.raw if seg else ""

    def get_indent_impulse(self) -> Tuple[int, int]:
        """Get the change in intended indent balance from this point.

        Returns:
            :obj:`tuple` of :obj:`int`: The first value is the raw
                impulse. The second is the deepest trough in the indent
                through the values to allow wiping of buffers.
        """
        trough = 0
        running_sum = 0
        for seg in self.segments:
            if seg.is_type("indent"):
                running_sum += cast(Indent, seg).indent_val
            if running_sum < trough:
                trough = running_sum
        return running_sum, trough

    def indent_to(
        self,
        desired_indent: str,
        after: Optional[BaseSegment] = None,
        before: Optional[BaseSegment] = None,
        description: Optional[str] = None,
    ) -> Tuple[List[LintFix], "ReflowPoint"]:
        """Coerce a point to have a particular indent.

        If the point currently contains no newlines, one will
        be introduced and any trailing whitespace will be effectively
        removed.

        More specifically, the newline is *inserted before* the existing
        whitespace, with the new indent being a *replacement* for that
        same whitespace.

        For placeholder newlines or indents we generate appropriate
        source fixes.
        """
        assert "\n" not in desired_indent, "Newline found in desired indent."
        # Get the indent (or in the case of no newline, the last whitespace)
        indent_seg = self._get_indent_segment()
        reflow_logger.debug(
            "Coercing indent %s to %r. (newlines: %s)",
            indent_seg,
            desired_indent,
            self.num_newlines(),
        )

        if indent_seg and indent_seg.is_type("placeholder"):
            # Handle the placeholder case.
            indent_seg = cast(TemplateSegment, indent_seg)
            # There should always be a newline, so assert that.
            assert "\n" in indent_seg.source_str
            # We should always replace the section _containing_ the
            # newline, rather than just bluntly inserting. This
            # makes slicing later easier.
            current_indent = indent_seg.source_str.split("\n")[-1]
            source_slice = slice(
                # Minus _one more_ for to cover the newline too.
                indent_seg.pos_marker.source_slice.stop - len(current_indent) - 1,
                indent_seg.pos_marker.source_slice.stop,
            )
            new_placeholder = indent_seg.edit(
                source_fixes=[
                    SourceFix(
                        "\n" + desired_indent,
                        source_slice,
                        # The templated slice is going to be a zero slice _anyway_.
                        indent_seg.pos_marker.templated_slice,
                    )
                ],
                source_str=indent_seg.source_str[: -len(current_indent)]
                + desired_indent,
            )
            new_fixes = [
                LintFix.replace(
                    indent_seg,
                    [new_placeholder],
                    description=description
                    or f"Expected {_indent_description(desired_indent)}.",
                )
            ]
            new_segments = [
                new_placeholder if seg is indent_seg else seg for seg in self.segments
            ]
            return new_fixes, ReflowPoint(tuple(new_segments))

        elif self.num_newlines():
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
                    return [
                        LintFix.delete(
                            indent_seg,
                            description=description or "Line should not be indented.",
                        )
                    ], ReflowPoint(self.segments[:idx] + self.segments[idx + 1 :])

                # Standard case of an indent change.
                new_indent = indent_seg.edit(desired_indent)
                idx = self.segments.index(indent_seg)
                return [
                    LintFix.replace(
                        indent_seg,
                        [new_indent],
                        description=description
                        or f"Expected {_indent_description(desired_indent)}.",
                    )
                ], ReflowPoint(
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
                # Rather than doing a `create_after` here, we're
                # going to do a replace. This is effectively to give a hint
                # to the linter that this is safe to do before a templated
                # placeholder. This solves some potential bugs - although
                # it feels a bit like a workaround.
                return [
                    LintFix.replace(
                        self.segments[idx],
                        [self.segments[idx], new_indent],
                        description=description
                        or f"Expected {_indent_description(desired_indent)}.",
                    )
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
                # Prefer anchoring before because it makes the labelling better.
                elif before:
                    before_raw = (
                        cast(TemplateSegment, before).source_str
                        if before.is_type("placeholder")
                        else before.raw
                    )
                    fix = LintFix.create_before(
                        before,
                        [new_newline, new_indent],
                        description=description
                        or (
                            "Expected line break and "
                            f"{_indent_description(desired_indent)} "
                            f"before {before_raw!r}."
                        ),
                    )
                else:
                    assert after  # mypy hint
                    after_raw = (
                        cast(TemplateSegment, after).source_str
                        if after.is_type("placeholder")
                        else after.raw
                    )
                    fix = LintFix.create_after(
                        after,
                        [new_newline, new_indent],
                        description=description
                        or (
                            "Expected line break and "
                            f"{_indent_description(desired_indent)} "
                            f"after {after_raw!r}."
                        ),
                    )
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
                if not description:
                    # Prefer before, because it makes the anchoring better.
                    if before:
                        description = (
                            "Expected line break and "
                            f"{_indent_description(desired_indent)} "
                            f"before {before.raw!r}."
                        )
                    elif after:
                        description = (
                            "Expected line break and "
                            f"{_indent_description(desired_indent)} "
                            f"after {after.raw!r}."
                        )
                    else:  # pragma: no cover
                        # NOTE: Doesn't have test coverage because there's
                        # normally an `after` or `before` value, so this
                        # clause is unused.
                        description = (
                            "Expected line break and "
                            f"{_indent_description(desired_indent)}."
                        )
                fix = LintFix.replace(ws_seg, new_segs, description=description)
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
        line breaks. The default operation of `respace` does not enable it,
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
