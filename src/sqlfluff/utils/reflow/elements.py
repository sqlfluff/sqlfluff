"""Dataclasses for reflow work."""

import logging
from dataclasses import dataclass, field
from itertools import chain
from typing import Dict, List, Optional, Sequence, Set, Tuple, Type, Union, cast

from sqlfluff.core.helpers.slice import slice_overlaps
from sqlfluff.core.parser import PositionMarker
from sqlfluff.core.parser.segments import (
    BaseSegment,
    Indent,
    NewlineSegment,
    RawSegment,
    SourceFix,
    TemplateSegment,
    WhitespaceSegment,
)
from sqlfluff.core.rules import LintFix, LintResult
from sqlfluff.utils.reflow.config import ReflowConfig
from sqlfluff.utils.reflow.depthmap import DepthInfo

# Respace Algorithms
from sqlfluff.utils.reflow.respace import (
    determine_constraints,
    handle_respace__inline_with_space,
    handle_respace__inline_without_space,
    process_spacing,
)

# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


def get_consumed_whitespace(segment: Optional[RawSegment]) -> Optional[str]:
    """A helper function to extract possible consumed whitespace.

    Args:
        segment (:obj:`RawSegment`, optional): A segment to test for
            suitability and extract the source representation of if
            appropriate. If passed None, then returns None.

    Returns:
        Returns the :code:`source_str` if the segment is of type
        :code:`placeholder` and has a :code:`block_type` of
        :code:`literal`. Otherwise None.
    """
    if not segment or not segment.is_type("placeholder"):
        return None
    placeholder = cast(TemplateSegment, segment)
    if placeholder.block_type != "literal":
        return None
    return placeholder.source_str


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

    @property
    def pos_marker(self) -> Optional[PositionMarker]:
        """Get the first position marker of the element."""
        for seg in self.segments:
            if seg.pos_marker:
                return seg.pos_marker
        return None

    def num_newlines(self) -> int:
        """Return the number of newlines in this element.

        These newlines are either newline segments or contained
        within consumed sections of whitespace. This counts
        both.
        """
        return sum(
            bool("newline" in seg.class_types)
            + (get_consumed_whitespace(seg) or "").count("\n")
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
    """Construct a human readable description of the indent.

    NOTE: We operate assuming that the "correct" indent is
    never a mix of tabs and spaces. That means if the provided
    indent *does* contain both that this description is likely
    a case where we are matching a pre-existing indent, and can
    assume that the *description* of that indent is non-critical.
    To handle that situation gracefully we just return "Mixed Indent".

    See: https://github.com/sqlfluff/sqlfluff/issues/4255
    """
    if indent == "":
        return "no indent"
    elif " " in indent and "\t" in indent:
        return "mixed indent"
    elif indent[0] == " ":
        assert all(c == " " for c in indent)
        return f"indent of {len(indent)} spaces"
    elif indent[0] == "\t":  # pragma: no cover
        assert all(c == "\t" for c in indent)
        return f"indent of {len(indent)} tabs"
    else:  # pragma: no cover
        raise NotImplementedError(f"Invalid indent construction: {indent!r}")


@dataclass(frozen=True)
class IndentStats:
    """Dataclass to hold summary of indents in a point.

    Attributes:
        impulse (int): The net change when summing the impulses
            of all the consecutive indent or dedent segments in
            a point.
        trough (int): The lowest point reached when summing the
            impulses (in order) of all the consecutive indent or
            dedent segments in a point.
        implicit_indents (tuple of int): The indent balance
            corresponding to any detected (and enabled) implicit
            indents. This follows the usual convention that indents
            are identified by their "uphill" side. A positive indent
            is identified by the indent balance _after_ and a negative
            indent is identified by the indent balance _before_.
    """

    impulse: int
    trough: int
    # Defaults to an empty tuple if unset.
    implicit_indents: Tuple[int, ...] = ()

    @classmethod
    def from_combination(
        cls, first: Optional["IndentStats"], second: "IndentStats"
    ) -> "IndentStats":
        """Create IndentStats from two consecutive IndentStats.

        This is mostly used for combining the effects of indent and dedent
        tokens either side of a comment.

        NOTE: The *first* is considered optional, because if we're
        calling this function, we're assuming that there's always
        a second.
        """
        # First check for the trivial case that we only have one.
        if not first:
            return second

        # Otherwise, combine the two into one.
        return cls(
            first.impulse + second.impulse,
            min(first.trough, first.impulse + second.trough),
            second.implicit_indents,
        )


@dataclass(frozen=True, init=False)
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

    _stats: IndentStats = field(init=False)

    def __init__(self, segments: Tuple[RawSegment, ...]):
        """Override the init method to calculate indent stats."""
        object.__setattr__(self, "segments", segments)
        object.__setattr__(self, "_stats", self._generate_indent_stats(segments))

    def _get_indent_segment(self) -> Optional[RawSegment]:
        """Get the current indent segment (if there).

        NOTE: This only returns _untemplated_ indents. If templated
        newline or whitespace segments are found they are skipped.
        """
        indent = None
        for seg in reversed(self.segments):
            if seg.pos_marker and not seg.pos_marker.is_literal():
                # Skip any templated elements.
                # NOTE: It must _have_ a position marker at this
                # point however to take this route. A segment
                # without a position marker at all, is an edit
                # or insertion, and so should still be considered.
                continue
            elif seg.is_type("newline"):
                return indent
            elif seg.is_type("whitespace"):
                indent = seg
            elif "\n" in (get_consumed_whitespace(seg) or ""):
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
        consumed_whitespace = get_consumed_whitespace(seg)
        if consumed_whitespace:  # pragma: no cover
            # Return last bit after newline.
            # NOTE: Not tested, because usually this would happen
            # directly via _get_indent_segment.
            return consumed_whitespace.split("\n")[-1]
        return seg.raw if seg else ""

    @staticmethod
    def _generate_indent_stats(
        segments: Sequence[RawSegment],
    ) -> IndentStats:
        """Generate the change in intended indent balance.

        This is the main logic which powers .get_indent_impulse()
        """
        trough = 0
        running_sum = 0
        implicit_indents = []
        for seg in segments:
            if seg.is_type("indent"):
                indent_seg = cast(Indent, seg)
                running_sum += indent_seg.indent_val
                # Do we need to add a new implicit indent?
                if indent_seg.is_implicit:
                    implicit_indents.append(running_sum)
                # NOTE: We don't check for removal of implicit indents
                # because it's unlikely that one would be opened, and then
                # closed within the same point. That would probably be the
                # sign of a bug in the dialect.
            if running_sum < trough:
                trough = running_sum
        return IndentStats(running_sum, trough, tuple(implicit_indents))

    def get_indent_impulse(self) -> IndentStats:
        """Get the change in intended indent balance from this point."""
        return self._stats

    def indent_to(
        self,
        desired_indent: str,
        after: Optional[BaseSegment] = None,
        before: Optional[BaseSegment] = None,
        description: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Tuple[List[LintResult], "ReflowPoint"]:
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
                indent_seg.pos_marker.source_slice.stop - len(current_indent),
                indent_seg.pos_marker.source_slice.stop,
            )
            for existing_source_fix in indent_seg.source_fixes:  # pragma: no cover
                if slice_overlaps(existing_source_fix.source_slice, source_slice):
                    reflow_logger.warning(
                        "Creating overlapping source fix. Results may be "
                        "unpredictable and this might be a sign of a bug. "
                        "Please report this along with your query.\n"
                        f"({existing_source_fix.source_slice} overlaps "
                        f"{source_slice})"
                    )

            new_source_fix = SourceFix(
                desired_indent,
                source_slice,
                # The templated slice is going to be a zero slice _anyway_.
                indent_seg.pos_marker.templated_slice,
            )

            if new_source_fix in indent_seg.source_fixes:  # pragma: no cover
                # NOTE: If we're trying to reapply the same fix, don't.
                # Just return an error without the fixes. This is probably
                # a bug if we're taking this route, but this clause will help
                # catch bugs faster if they occur.
                reflow_logger.warning(
                    "Attempted to apply a duplicate source fix to %r. "
                    "Returning this time without fix.",
                    indent_seg.pos_marker.source_str(),
                )
                fixes = []
                new_segments = self.segments
            else:
                if current_indent:
                    new_source_str = (
                        indent_seg.source_str[: -len(current_indent)] + desired_indent
                    )
                else:
                    new_source_str = indent_seg.source_str + desired_indent
                assert "\n" in new_source_str
                new_placeholder = indent_seg.edit(
                    source_fixes=[new_source_fix],
                    source_str=new_source_str,
                )
                fixes = [LintFix.replace(indent_seg, [new_placeholder])]
                new_segments = tuple(
                    new_placeholder if seg is indent_seg else seg
                    for seg in self.segments
                )

            return [
                LintResult(
                    indent_seg,
                    fixes,
                    description=description
                    or f"Expected {_indent_description(desired_indent)}.",
                    source=source,
                )
            ], ReflowPoint(new_segments)

        elif self.num_newlines():
            # There is already a newline. Is there an indent?
            if indent_seg:
                # Coerce existing indent to desired.
                if indent_seg.raw == desired_indent:
                    # Trivial case. Indent already correct
                    return [], self
                elif desired_indent == "":
                    idx = self.segments.index(indent_seg)
                    return [
                        LintResult(
                            indent_seg,
                            # Coerce to no indent. We don't want the indent. Delete it.
                            [LintFix.delete(indent_seg)],
                            description=description or "Line should not be indented.",
                            source=source,
                        )
                    ], ReflowPoint(self.segments[:idx] + self.segments[idx + 1 :])

                # Standard case of an indent change.
                new_indent = indent_seg.edit(desired_indent)
                idx = self.segments.index(indent_seg)
                return [
                    LintResult(
                        indent_seg,
                        [LintFix.replace(indent_seg, [new_indent])],
                        description=description
                        or f"Expected {_indent_description(desired_indent)}.",
                        source=source,
                    )
                ], ReflowPoint(
                    self.segments[:idx] + (new_indent,) + self.segments[idx + 1 :]
                )

            else:
                # There is a newline, but no indent. Make one after the newline
                # Find the index of the last newline (there _will_ be one because
                # we checked self.num_newlines() above).

                # Before going further, check we have a non-zero indent.
                if not desired_indent:
                    # We're trying to coerce a non-existent indent to zero. This
                    # means we're already ok.
                    return [], self

                for idx in range(len(self.segments) - 1, -1, -1):
                    # NOTE: Must be a _literal_ newline, not a templated one.
                    # https://github.com/sqlfluff/sqlfluff/issues/4367
                    if self.segments[idx].is_type("newline"):
                        if self.segments[idx].pos_marker.is_literal():
                            break

                new_indent = WhitespaceSegment(desired_indent)
                return [
                    LintResult(
                        # The anchor for the *result* should be the segment
                        # *after* the newline, otherwise the location of the fix
                        # is confusing.
                        # For this method, `before` is optional, but normally
                        # passed. If it is there, use that as the anchor
                        # instead. We fall back to the last newline if not.
                        before if before else self.segments[idx],
                        # Rather than doing a `create_after` here, we're
                        # going to do a replace. This is effectively to give a hint
                        # to the linter that this is safe to do before a templated
                        # placeholder. This solves some potential bugs - although
                        # it feels a bit like a workaround.
                        [
                            LintFix.replace(
                                self.segments[idx], [self.segments[idx], new_indent]
                            )
                        ],
                        description=description
                        or f"Expected {_indent_description(desired_indent)}.",
                        source=source,
                    )
                ], ReflowPoint(
                    self.segments[: idx + 1] + (new_indent,) + self.segments[idx + 1 :]
                )

        else:
            # There isn't currently a newline.
            new_newline = NewlineSegment()
            new_segs: List[RawSegment]
            # Check for whitespace
            ws_seg = None
            for seg in self.segments[::-1]:
                if seg.is_type("whitespace"):
                    ws_seg = seg
            if not ws_seg:
                # Work out the new segments. Always a newline, only whitespace if
                # there's a non zero indent.
                new_segs = [new_newline] + (
                    [WhitespaceSegment(desired_indent)] if desired_indent else []
                )
                # There isn't a whitespace segment either. We need to insert one.
                # Do we have an anchor?
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
                    fix = LintFix.create_before(before, new_segs)
                    description = description or (
                        "Expected line break and "
                        f"{_indent_description(desired_indent)} "
                        f"before {before_raw!r}."
                    )
                else:
                    assert after  # mypy hint
                    after_raw = (
                        cast(TemplateSegment, after).source_str
                        if after.is_type("placeholder")
                        else after.raw
                    )
                    fix = LintFix.create_after(after, new_segs)
                    description = description or (
                        "Expected line break and "
                        f"{_indent_description(desired_indent)} "
                        f"after {after_raw!r}."
                    )
                new_point = ReflowPoint(tuple(new_segs))
                anchor = before
            else:
                # There is whitespace. Coerce it to the right indent and add
                # a newline _before_. In the edge case that we're coercing to
                # _no indent_, edit existing indent to be the newline and leave
                # it there.
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
                fix = LintFix.replace(ws_seg, new_segs)
                new_point = ReflowPoint(
                    self.segments[:idx] + tuple(new_segs) + self.segments[idx + 1 :]
                )
                anchor = ws_seg

            return [
                LintResult(anchor, fixes=[fix], description=description, source=source)
            ], new_point

    def respace_point(
        self,
        prev_block: Optional[ReflowBlock],
        next_block: Optional[ReflowBlock],
        root_segment: BaseSegment,
        lint_results: List[LintResult],
        strip_newlines: bool = False,
        anchor_on: str = "before",
    ) -> Tuple[List[LintResult], "ReflowPoint"]:
        """Respace a point based on given constraints.

        NB: This effectively includes trailing whitespace fixes.

        Deletion and edit fixes are generated immediately, but creations
        are paused to the end and done in bulk so as not to generate conflicts.

        Note that the `strip_newlines` functionality exists here as a slight
        exception to pure respacing, but as a very simple case of positioning
        line breaks. The default operation of `respace` does not enable it,
        however it exists as a convenience for rules which wish to use it.
        """
        existing_results = lint_results[:]
        pre_constraint, post_constraint, strip_newlines = determine_constraints(
            prev_block, next_block, strip_newlines
        )

        reflow_logger.debug("* Respacing: %r @ %s", self.raw, self.pos_marker)

        # The buffer is used to create the new reflow point to return
        segment_buffer, last_whitespace, new_results = process_spacing(
            list(self.segments), strip_newlines
        )

        # Check for final trailing whitespace (which otherwise looks like an indent).
        if next_block and "end_of_file" in next_block.class_types and last_whitespace:
            new_results.append(
                LintResult(
                    last_whitespace,
                    [LintFix.delete(last_whitespace)],
                    description="Unnecessary trailing whitespace at end of file.",
                )
            )
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
            if last_whitespace:
                ws_idx = self.segments.index(last_whitespace)
                if ws_idx > 0:
                    # NOTE: Iterate by index so that we don't slice the full range.
                    for prev_seg_idx in range(ws_idx - 1, -1, -1):
                        prev_seg = self.segments[prev_seg_idx]
                        # Skip past any indents
                        if not prev_seg.is_type("indent"):
                            break

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
                        # Ideally we should attach to an existing result.
                        # To do that effectively, we should look for the removed
                        # segment in the existing results.
                        temp_idx = last_whitespace.pos_marker.templated_slice.start
                        for res in existing_results:
                            if (
                                res.anchor
                                and res.anchor.pos_marker
                                and res.anchor.pos_marker.templated_slice.stop
                                == temp_idx
                            ):
                                break
                        else:  # pragma: no cover
                            raise NotImplementedError("Could not find removal result.")
                        existing_results.remove(res)
                        new_results.append(
                            LintResult(
                                res.anchor,
                                fixes=res.fixes + [LintFix("delete", last_whitespace)],
                                description=res.description,
                            )
                        )
            # Return the results.
            return existing_results + new_results, ReflowPoint(tuple(segment_buffer))

        # Otherwise is this an inline case? (i.e. no newline)
        reflow_logger.debug(
            "    Inline case. Constraints: %s <-> %s.",
            pre_constraint,
            post_constraint,
        )

        # Do we at least have _some_ whitespace?
        if last_whitespace:
            # We do - is it the right size?
            segment_buffer, results = handle_respace__inline_with_space(
                pre_constraint,
                post_constraint,
                prev_block,
                next_block,
                root_segment,
                segment_buffer,
                last_whitespace,
            )
            new_results.extend(results)
        else:
            # No. Should we insert some?
            # NOTE: This method operates on the existing fix buffer.
            segment_buffer, new_results, edited = handle_respace__inline_without_space(
                pre_constraint,
                post_constraint,
                prev_block,
                next_block,
                segment_buffer,
                existing_results + new_results,
                anchor_on=anchor_on,
            )
            existing_results = []
            if edited:
                reflow_logger.debug("    Modified result buffer: %s", new_results)

        # Only log if we actually made a change.
        if new_results:
            reflow_logger.debug("    New Results: %s", new_results)

        return existing_results + new_results, ReflowPoint(tuple(segment_buffer))


ReflowSequenceType = List[Union[ReflowBlock, ReflowPoint]]
