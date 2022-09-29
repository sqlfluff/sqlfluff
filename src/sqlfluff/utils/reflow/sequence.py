"""Dataclasses for reflow work."""


from dataclasses import dataclass
from itertools import chain
import logging
from typing import Iterator, List, Optional, Sequence, Tuple, cast, Type, Union
from sqlfluff.core.config import FluffConfig

from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.rules.base import LintFix
from sqlfluff.utils.reflow.config import ReflowConfig
from sqlfluff.utils.reflow.depthmap import DepthMap

from sqlfluff.utils.reflow.elements import ReflowBlock, ReflowPoint

# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")
ReflowSequenceType = List[Union[ReflowBlock, ReflowPoint]]


@dataclass(frozen=True)
class _RebreakSpan:
    """A location within a sequence to consider rebreaking."""

    target: BaseSegment
    start_idx: int
    end_idx: int
    line_position: str
    strict: bool


@dataclass(frozen=True)
class _RebreakLocation:
    """A location within a sequence to rebreak, with metadata."""

    target: BaseSegment
    prev_code_pt_idx: int
    prev_nl_idx: int
    prev_point_idx: int
    next_point_idx: int
    next_nl_idx: int
    next_code_pt_idx: int
    line_position: str
    strict: bool

    @classmethod
    def from_span(cls, span: _RebreakSpan, elements: ReflowSequenceType):
        """Expand a span to a location."""
        # First get the next newline.
        prev_point_idx = span.start_idx - 1
        next_point_idx = span.end_idx + 1

        prev_nl_idx = prev_point_idx
        next_nl_idx = next_point_idx
        # We hop in 2s because we're checking two ahead.
        while (
            prev_nl_idx >= 2
            and "newline" not in elements[prev_nl_idx].class_types
            and not any(seg.is_code for seg in elements[prev_nl_idx - 1].segments)
        ):
            prev_nl_idx -= 2
        while (
            next_nl_idx < len(elements) - 2
            and "newline" not in elements[next_nl_idx].class_types
            and not any(seg.is_code for seg in elements[next_nl_idx + 1].segments)
        ):
            next_nl_idx += 2
        # Then just find the next code
        prev_code_pt_idx = prev_nl_idx
        next_code_pt_idx = next_nl_idx
        # We hop in 2s because we're checking two ahead.
        while next_code_pt_idx < len(elements) - 2 and not any(
            seg.is_code for seg in elements[next_code_pt_idx + 1].segments
        ):
            next_code_pt_idx += 2
        while prev_code_pt_idx >= 2 and not any(
            seg.is_code for seg in elements[prev_code_pt_idx - 1].segments
        ):
            prev_code_pt_idx -= 2
        return cls(
            span.target,
            prev_code_pt_idx,
            prev_nl_idx,
            prev_point_idx,
            next_point_idx,
            next_nl_idx,
            next_code_pt_idx,
            span.line_position,
            span.strict,
        )

    def has_templated_newline(self, elements: ReflowSequenceType) -> bool:
        """Is either side a templated newline?

        If either side has a templated newline, then that's ok too.
        The intent here is that if the next newline is a _templated_
        one, then in the source there will be a tag ({{ tag }}), which
        acts like _not having a newline_.
        """
        # Check the _last_ newline of the previous point.
        # Slice backward to search in reverse.
        for seg in elements[self.prev_nl_idx].segments[::-1]:
            if seg.is_type("newline"):
                if not seg.pos_marker.is_literal():
                    return True
                break
        # Check the _first_ newline of the next point.
        for seg in elements[self.next_nl_idx].segments:
            if seg.is_type("newline"):
                if not seg.pos_marker.is_literal():
                    return True
                break
        return False

    def has_inappropriate_newlines(
        self, elements: ReflowSequenceType, strict: bool = False
    ) -> bool:
        """Is the span surrounded by one (but not two) line breaks?

        Args:
            elements: The elements of the ReflowSequence this element
               is taken from to allow comparison.
            strict (:obj:`bool`): If set to true, this will not allow
               the case where there aren't newlines on either side.
        """
        # Here we use the newline index, not
        # just the adjacent point, so that we can see past comments.
        n_prev_newlines = elements[self.prev_nl_idx].num_newlines()
        n_next_newlines = elements[self.next_nl_idx].num_newlines()
        return (
            # If there isn't a newline on either side then carry
            # on, unless it's strict.
            not bool(n_prev_newlines or n_next_newlines or strict)
            # If there is a newline on BOTH sides. That's ok.
            or bool(n_prev_newlines and n_next_newlines)
        )


class ReflowSequence:
    """Class for keeping track of elements in a reflow operation.

    It is assumed that there will be alternating blocks and points
    (even if some points have no segments). This is validated on
    construction.

    We assume points on each end because this is the case with a file.
    """

    def __init__(
        self,
        elements: ReflowSequenceType,
        root_segment: BaseSegment,
        reflow_config: ReflowConfig,
        depth_map: DepthMap,
        embodied_fixes: Optional[List[LintFix]] = None,
    ):
        # First validate integrity
        self._validate_reflow_sequence(elements)
        # Then save
        self.elements = elements
        self.root_segment = root_segment
        self.reflow_config = reflow_config
        self.depth_map = depth_map
        # This keeps track of fixes generated in the chaining process.
        # Alternatively pictured: This is the list of fixes required
        # to generate this sequence. We can build on this as we edit
        # the sequence.
        self.embodied_fixes: List[LintFix] = embodied_fixes or []

    def get_fixes(self):
        """Get the current fix buffer."""
        return self.embodied_fixes

    def get_raw(self):
        """Get the current raw representation."""
        return "".join(elem.raw for elem in self.elements)

    @staticmethod
    def _validate_reflow_sequence(elements: ReflowSequenceType):
        assert elements, "ReflowSequence has empty elements."
        # Check odds and evens
        OddType = elements[0].__class__
        EvenType = ReflowPoint if OddType is ReflowBlock else ReflowBlock
        try:
            # Check odds are all points
            assert all(
                isinstance(elem, OddType) for elem in elements[::2]
            ), f"Not all odd elements are {OddType.__name__}"
            # Check evens are all blocks
            assert all(
                isinstance(elem, EvenType) for elem in elements[1::2]
            ), f"Not all even elements are {EvenType.__name__}"
        except AssertionError as err:  # pragma: no cover
            for elem in elements:
                reflow_logger.error("   - %s", elem)
            reflow_logger.exception("Assertion check on ReflowSequence failed.")
            raise err

    @staticmethod
    def _elements_from_raw_segments(
        segments: Sequence[RawSegment], reflow_config: ReflowConfig, depth_map: DepthMap
    ) -> ReflowSequenceType:
        """Construct reflow elements from raw segments.

        NOTE: ReflowBlock elements should only ever have one segment
        which simplifies iteration here.
        """
        elem_buff: ReflowSequenceType = []
        seg_buff: List[RawSegment] = []
        for seg in segments:
            # NOTE: end_of_file is block-like rather than point-like.
            # This is to facilitate better evaluation of the ends of files.
            if seg.is_type("whitespace", "newline", "indent"):
                # Add to the buffer and move on.
                seg_buff.append(seg)
                continue
            elif elem_buff or seg_buff:
                # There are elements. The last will have been a block.
                # Add a point before we add the block. NOTE: It may be empty.
                elem_buff.append(ReflowPoint(segments=seg_buff))
            # Add the block, with config info.
            elem_buff.append(
                ReflowBlock.from_config(
                    segments=[seg],
                    config=reflow_config,
                    depth_info=depth_map.get_depth_info(seg),
                )
            )
            # Empty the buffer
            seg_buff = []

        # If we ended with a buffer, apply it.
        # TODO: Consider removing this clause?
        if seg_buff:  # pragma: no cover
            elem_buff.append(ReflowPoint(segments=seg_buff))
        return elem_buff

    @classmethod
    def from_raw_segments(
        cls: Type["ReflowSequence"],
        segments: Sequence[RawSegment],
        root_segment: BaseSegment,
        config: FluffConfig,
        depth_map: Optional[DepthMap] = None,
    ) -> "ReflowSequence":
        """Construct a ReflowSequence from a sequence of raw segments.

        Aimed to be the basic constructor, which other more specific
        ones may fall back to.
        """
        reflow_config = ReflowConfig.from_fluff_config(config)
        if depth_map is None:
            depth_map = DepthMap.from_raws_and_root(segments, root_segment)
        return cls(
            elements=cls._elements_from_raw_segments(
                segments,
                reflow_config=reflow_config,
                # NOTE: This pathway is inefficient. Ideally the depth
                # map should be constructed elsewhere and then passed in.
                depth_map=depth_map,
            ),
            root_segment=root_segment,
            reflow_config=reflow_config,
            depth_map=depth_map,
        )

    @classmethod
    def from_root(
        cls: Type["ReflowSequence"], root_segment: BaseSegment, config: FluffConfig
    ) -> "ReflowSequence":
        """Generate a sequence from a root segment."""
        return cls.from_raw_segments(
            root_segment.raw_segments,
            root_segment,
            config=config,
            # This is the efficient route. We use it here because we can.
            depth_map=DepthMap.from_parent(root_segment),
        )

    @classmethod
    def from_around_target(
        cls: Type["ReflowSequence"],
        target_segment: BaseSegment,
        root_segment: BaseSegment,
        config: FluffConfig,
        sides: str = "both",
    ) -> "ReflowSequence":
        """Generate a sequence around a target.

        Args:
            target_segment (:obj:`RawSegment`): The segment to center
                around when considering the sequence to construct.
            root_segment (:obj:`BaseSegment`): The relevant root
                segment (usually the base :obj:`FileSegment`).
            config (:obj:`FluffConfig`): A config object from which
                to load the spacing behaviours of different segments.
            sides (:obj:`str`): Limit the reflow sequence to just one
                side of the target. Default is two sided ("both"), but
                set to "before" or "after" to limit to either side.


        NOTE: We don't just expand to the first block around the
        target but to the first _code_ element, which means we
        may swallow several `comment` blocks in the process.

        To evaluate reflow around a specific target, we need
        need to generate a sequence which goes for the preceding
        raw to the following raw.
        i.e. at least: block - point - block - point - block
        (where the central block is the target).
        """
        # There's probably a more efficient way than immediately
        # materialising the raw_segments for the whole root, but
        # it works. Optimise later.
        all_raws = root_segment.raw_segments

        target_raws = target_segment.raw_segments
        assert target_raws
        pre_idx = all_raws.index(target_raws[0])
        post_idx = all_raws.index(target_raws[-1]) + 1
        initial_idx = (pre_idx, post_idx)
        if sides in ("both", "before"):
            # Catch at least the previous segment
            pre_idx -= 1
            while pre_idx - 1 > 0 and not all_raws[pre_idx].is_code:
                pre_idx -= 1
        if sides in ("both", "after"):
            while post_idx < len(all_raws) and not all_raws[post_idx].is_code:
                post_idx += 1
            # Capture one more after the whitespace.
            post_idx += 1
        segments = all_raws[pre_idx:post_idx]
        reflow_logger.debug(
            "Generating ReflowSequence.from_around_target(). idx: %s. "
            "slice: %s:%s. raw: %r",
            initial_idx,
            pre_idx,
            post_idx,
            "".join(seg.raw for seg in segments),
        )
        return cls.from_raw_segments(segments, root_segment, config=config)

    def _find_element_idx_with(self, target: RawSegment) -> int:
        for idx, elem in enumerate(self.elements):
            if target in elem.segments:
                return idx
        raise ValueError(  # pragma: no cover
            f"Target [{target}] not found in ReflowSequence."
        )

    def without(self, target: RawSegment) -> "ReflowSequence":
        """Returns a new reflow sequence without the specified segment.

        It's important to note that this doesn't itself remove the target
        from the file. This just allows us to simulate a sequence without it
        and work out what additional whitespace changes would be required
        if we were to remove it.
        """
        removal_idx = self._find_element_idx_with(target)
        if removal_idx == 0 or removal_idx == len(self.elements) - 1:
            raise NotImplementedError(  # pragma: no cover
                "Unexpected removal at one end of a ReflowSequence."
            )
        if isinstance(self.elements[removal_idx], ReflowPoint):
            raise NotImplementedError(  # pragma: no cover
                "Not expected removal of whitespace in ReflowSequence."
            )
        merged_point = ReflowPoint(
            segments=list(self.elements[removal_idx - 1].segments)
            + list(self.elements[removal_idx + 1].segments),
        )
        return ReflowSequence(
            elements=self.elements[: removal_idx - 1]
            + [merged_point]
            + self.elements[removal_idx + 2 :],
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            # Generate the fix to do the removal.
            embodied_fixes=[LintFix.delete(target)],
        )

    def insert(
        self, insertion: RawSegment, target: RawSegment, pos: str = "before"
    ) -> "ReflowSequence":
        """Returns a new reflow sequence with the new element inserted.

        Insertion is always relative to an existing element. Either before
        or after it as specified by `pos`.
        """
        assert pos in ("before", "after")
        target_idx = self._find_element_idx_with(target)
        # Are we trying to insert something whitespace-like?
        if insertion.is_type("whitespace", "indent", "newline"):  # pragma: no cover
            raise ValueError(
                "ReflowSequence.insert() does not support direct insertion of "
                "spacing elements such as whitespace or newlines"
            )

        # We're inserting something blocky. That means a new block AND a new point.
        # It's possible we try to _split_ a point by targeting a whitespace element
        # inside a larger point. For now this isn't supported.
        # NOTE: We use the depth info of the reference anchor, with the assumption
        # (I think reliable) that the insertion will be applied as a sibling of
        # the target.
        self.depth_map.copy_depth_info(target, insertion)
        new_block = ReflowBlock.from_config(
            segments=[insertion],
            config=self.reflow_config,
            depth_info=self.depth_map.get_depth_info(target),
        )
        if isinstance(self.elements[target_idx], ReflowPoint):
            raise NotImplementedError(  # pragma: no cover
                "Can't insert relative to whitespace for now."
            )
        elif pos == "before":
            return ReflowSequence(
                elements=self.elements[:target_idx]
                + [new_block, ReflowPoint([])]
                + self.elements[target_idx:],
                root_segment=self.root_segment,
                reflow_config=self.reflow_config,
                depth_map=self.depth_map,
                # Generate the fix to do the removal.
                embodied_fixes=[LintFix.create_before(target, [insertion])],
            )
        elif pos == "after":  # pragma: no cover
            # TODO: This doesn't get coverage - should it even exist?
            # Re-evaluate whether this code path is ever taken once more rules use
            # this.
            return ReflowSequence(
                elements=self.elements[: target_idx + 1]
                + [ReflowPoint([]), new_block]
                + self.elements[target_idx + 1 :],
                root_segment=self.root_segment,
                reflow_config=self.reflow_config,
                depth_map=self.depth_map,
                # Generate the fix to do the removal.
                embodied_fixes=[LintFix.create_after(target, [insertion])],
            )
        raise ValueError(
            f"Unexpected value for ReflowSequence.insert(pos): {pos}"
        )  # pragma: no cover

    def replace(
        self, target: BaseSegment, edit: Sequence[BaseSegment]
    ) -> "ReflowSequence":
        """Returns a new reflow sequence with `edit` elements replaced."""
        replace_fix = LintFix.replace(target, edit)

        target_raws = target.raw_segments
        assert target_raws

        edit_raws = list(chain.from_iterable(seg.raw_segments for seg in edit))

        # Add the new segments to the depth map at the same level as the target.
        # First work out how much to trim by.
        trim_amount = len(target.path_to(target_raws[0]))
        reflow_logger.debug(
            "Replacement trim amount: %s.",
            trim_amount,
        )
        for edit_raw in edit_raws:
            # NOTE: if target raws has more than one segment we take the depth info
            # of the first one. We trim to avoid including the implications of removed
            # "container" segments.
            self.depth_map.copy_depth_info(target_raws[0], edit_raw, trim=trim_amount)

        # It's much easier to just totally reconstruct the sequence rather
        # than do surgery on the elements.

        # TODO: The surgery is actually a good idea for long sequences now that
        # we have the depth map.

        current_raws = list(
            chain.from_iterable(elem.segments for elem in self.elements)
        )
        start_idx = current_raws.index(target_raws[0])
        last_idx = current_raws.index(target_raws[-1])

        return ReflowSequence(
            self._elements_from_raw_segments(
                current_raws[:start_idx] + edit_raws + current_raws[last_idx + 1 :],
                reflow_config=self.reflow_config,
                # NOTE: the depth map has been mutated to include the new segments.
                depth_map=self.depth_map,
            ),
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            embodied_fixes=[replace_fix],
        )

    def _iter_points_with_constraints(
        self,
    ) -> Iterator[Tuple[ReflowPoint, Optional[ReflowBlock], Optional[ReflowBlock]]]:
        for idx, elem in enumerate(self.elements):
            # Only evaluate points.
            if isinstance(elem, ReflowPoint):
                pre = None
                post = None
                if idx > 0:
                    pre = cast(ReflowBlock, self.elements[idx - 1])
                if idx < len(self.elements) - 1:
                    post = cast(ReflowBlock, self.elements[idx + 1])
                yield elem, pre, post

    def respace(
        self, strip_newlines: bool = False, filter: str = "all"
    ) -> "ReflowSequence":
        """Respace a sequence.

        Args:
            strip_newlines (:obj:`bool`): Optionally strip newlines
                before respacing. This is primarily used on focussed
                sequences to coerce objects onto a single line. This
                does not apply any prioritisation to which line breaks
                to remove and so is not a substitute for the full
                `reindent` or `reflow` methods.
            filter (:obj:`str`): Optionally filter which reflow points
                to respace. Default configuration is `all`. Other options
                are `line_break` which only respaces points containing
                a `newline` or followed by an `end_of_file` marker, or
                `inline` which is the inverse of `line_break`. This is
                most useful for filtering between trailing whitespace
                and fixes between content on a line.

        This resets spacing in a ReflowSequence. Note, it relies on the
        embodied fixes being correct so that we can build on them.
        """
        assert filter in (
            "all",
            "newline",
            "inline",
        ), f"Unexpected value for filter: {filter}"
        # Use the embodied fixes as a starting point.
        fixes = self.embodied_fixes or []
        new_elements: ReflowSequenceType = []
        for point, pre, post in self._iter_points_with_constraints():
            # We filter on the elements POST RESPACE. This is to allow
            # strict respacing to reclaim newlines.
            new_fixes, new_point = point.respace_point(
                prev_block=pre,
                next_block=post,
                root_segment=self.root_segment,
                fixes=fixes,
                strip_newlines=strip_newlines,
            )
            # If filter has been set, optionally unset the returned values.
            if (
                filter == "inline"
                if (
                    # NOTE: We test on the NEW point.
                    any(seg.is_type("newline") for seg in new_point.segments)
                    # Or if it's followed by the end of file
                    or (post and "end_of_file" in post.class_types)
                )
                else filter == "newline"
            ):
                # Reset the values
                reflow_logger.debug(
                    "    Filter %r applied. Resetting %s", filter, point
                )
                new_point = point
            # Otherwise apply the new fixes
            else:
                reflow_logger.debug(
                    "    Filter %r allows fixes for point: %s", filter, new_fixes
                )
                fixes = new_fixes

            if pre and (not new_elements or new_elements[-1] != pre):
                new_elements.append(pre)
            new_elements.append(new_point)
            if post:
                new_elements.append(post)
        return ReflowSequence(
            elements=new_elements,
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            # Generate the fix to do the removal.
            embodied_fixes=fixes,
        )

    @staticmethod
    def _identify_rebreak_spans(
        element_buffer: ReflowSequenceType, root_segment: BaseSegment
    ) -> List[_RebreakSpan]:
        spans: List[_RebreakSpan] = []
        # We'll need at least two elements each side, so constrain
        # our range accordingly.
        for idx in range(2, len(element_buffer) - 2):
            # Only evaluate blocks:
            elem = element_buffer[idx]
            # Only evaluate blocks
            if not isinstance(elem, ReflowBlock):
                continue
            # Does the element itself have config? (The easy case)
            if elem.line_position:
                # Blocks should only have one segment so it's easy to pick it.
                spans.append(
                    _RebreakSpan(
                        elem.segments[0],
                        idx,
                        idx,
                        # NOTE: this isn't pretty but until it needs to be more
                        # complex, this works.
                        elem.line_position.split(":")[0],
                        elem.line_position.endswith("strict"),
                    )
                )
            # Do any of it's parents have config, and are we at the start
            # of them?
            for key in elem.line_position_configs.keys():
                seg_idx, length, _ = elem.depth_info.stack_positions[key]
                # If we're not at the start of the segment, then pass.
                if seg_idx != 0:
                    continue
                # Can we find the end?
                for end_idx in range(idx, len(element_buffer) - 2):
                    end_elem = element_buffer[end_idx]
                    if not isinstance(end_elem, ReflowBlock):
                        continue
                    if end_elem.depth_info.stack_positions[key][0] == length - 1:
                        # Found the end. Add it to the stack.
                        # We reference the appropriate element from the parent stack.
                        target_depth = elem.depth_info.stack_hashes.index(key)
                        target = root_segment.path_to(element_buffer[idx].segments[0])[
                            target_depth
                        ].segment
                        spans.append(
                            _RebreakSpan(
                                target,
                                idx,
                                end_idx,
                                # NOTE: this isn't pretty but until it needs to be more
                                # complex, this works.
                                elem.line_position_configs[key].split(":")[0],
                                elem.line_position_configs[key].endswith("strict"),
                            )
                        )
                        break
                else:
                    # If we find the start, but not the end, it's not a problem, but
                    # we won't be rebreaking this span. This is important so that we
                    # don't rebreak part of something without the context of what's
                    # in the rest of it. Continue.
                    continue
        return spans

    def rebreak(self):
        """Reflow line breaks within a sequence.

        Initially this only _moves_ existing segments
        around line breaks (e.g. for operators and commas),
        but eventually this method should also handle line
        length considerations too.

        This intentionally does *not* handle indentation,
        as the existing indents are assumed to be correct.
        """
        if self.embodied_fixes:
            raise NotImplementedError(  # pragma: no cover
                "rebreak cannot currently handle pre-existing embodied fixes."
            )

        fixes = []
        elem_buff: ReflowSequenceType = self.elements.copy()

        # Given a sequence we should identify the objects which
        # make sense to rebreak. That includes any raws with config,
        # but also and parent segments which have config and we can
        # find both ends for. Given those spans, we then need to find
        # the points either side of them and then the blocks either
        # side to respace them at the same time.

        # 1. First find appropriate spans.
        spans = self._identify_rebreak_spans(self.elements, self.root_segment)

        # The spans give us the edges of operators, but for line positioning we need
        # to handle comments differently. There are two other important points:
        # 1. The next newline outward before code (but passing over comments).
        # 2. The point before the next _code_ segment (ditto comments).
        locations = [_RebreakLocation.from_span(span, self.elements) for span in spans]

        # Handle each span:
        for loc in locations:

            reflow_logger.debug(
                "Handing Rebreak Span (%r: %s): %r",
                loc.line_position,
                loc.target,
                "".join(
                    elem.raw
                    for elem in elem_buff[
                        loc.prev_code_pt_idx - 1 : loc.next_code_pt_idx + 2
                    ]
                ),
            )

            if loc.has_inappropriate_newlines(elem_buff, strict=loc.strict):
                continue

            if loc.has_templated_newline(elem_buff):
                continue

            # Points and blocks either side are just offsets from the indices.
            prev_point = elem_buff[loc.prev_point_idx]
            next_point = elem_buff[loc.next_point_idx]

            # So we know we have a preference, is it ok?
            if loc.line_position == "leading":
                if elem_buff[loc.prev_nl_idx].num_newlines():
                    # We're good. It's already leading.
                    continue
                # Is it the simple case with no comments between the
                # old and new desired locations and only a single following
                # whitespace?
                elif (
                    loc.next_point_idx == loc.next_code_pt_idx
                    and elem_buff[loc.next_nl_idx].num_newlines() == 1
                ):
                    reflow_logger.debug("  Trailing Easy Case")
                    # Simple case. No comments.
                    # Strip newlines from the next point. Apply the indent to
                    # the previous point.
                    fixes, prev_point = prev_point.indent_to(
                        next_point.get_indent() or "", before=loc.target
                    )
                    fixes, next_point = next_point.respace_point(
                        elem_buff[loc.next_point_idx - 1],
                        elem_buff[loc.next_point_idx + 1],
                        root_segment=self.root_segment,
                        fixes=fixes,
                        strip_newlines=True,
                    )
                    # Update the points in the buffer
                    elem_buff[loc.prev_point_idx] = prev_point
                    elem_buff[loc.next_point_idx] = next_point
                else:
                    reflow_logger.debug("  Trailing Tricky Case")
                    # Otherwise we've got a tricky scenario where there are comments
                    # to negotiate around. In this case, we _move the target_
                    # rather than just adjusting the whitespace.

                    # Delete the existing position of the target, and
                    # the _preceding_ point.
                    fixes.append(LintFix.delete(loc.target))
                    for seg in elem_buff[loc.prev_point_idx].segments:
                        fixes.append(LintFix.delete(seg))

                    # We re-insert always reinsert after the first point, but respace
                    # the inserted point to ensure it's the right size given
                    # configs.
                    fixes, new_point = ReflowPoint([]).respace_point(
                        elem_buff[loc.next_point_idx - 1],
                        elem_buff[loc.next_code_pt_idx + 1],
                        root_segment=self.root_segment,
                        fixes=fixes,
                        anchor_on="after",
                    )
                    fixes.append(
                        LintFix.create_after(
                            elem_buff[loc.next_code_pt_idx].segments[-1],
                            [loc.target],
                        )
                    )

                    elem_buff = (
                        elem_buff[: loc.prev_point_idx]
                        + elem_buff[loc.next_point_idx : loc.next_code_pt_idx + 1]
                        + elem_buff[
                            loc.prev_point_idx + 1 : loc.next_point_idx
                        ]  # the target
                        + [new_point]
                        + elem_buff[loc.next_code_pt_idx + 1 :]
                    )

            elif loc.line_position == "trailing":
                if elem_buff[loc.next_nl_idx].num_newlines():
                    # We're good, it's already trailing.
                    continue
                # Is it the simple case with no comments between the
                # old and new desired locations and only one previous newline?
                elif (
                    loc.prev_point_idx == loc.prev_code_pt_idx
                    and elem_buff[loc.prev_nl_idx].num_newlines() == 1
                ):
                    reflow_logger.debug("  Leading Easy Case")
                    # Simple case. No comments.
                    # Strip newlines from the previous point. Apply the indent
                    # to the next point.
                    fixes, next_point = next_point.indent_to(
                        prev_point.get_indent() or "", after=loc.target
                    )
                    fixes, prev_point = prev_point.respace_point(
                        elem_buff[loc.prev_point_idx - 1],
                        elem_buff[loc.prev_point_idx + 1],
                        root_segment=self.root_segment,
                        fixes=fixes,
                        strip_newlines=True,
                    )
                    # Update the points in the buffer
                    elem_buff[loc.prev_point_idx] = prev_point
                    elem_buff[loc.next_point_idx] = next_point
                else:
                    reflow_logger.debug("  Leading Tricky Case")
                    # Otherwise we've got a tricky scenario where there are comments
                    # to negotiate around. In this case, we _move the target_
                    # rather than just adjusting the whitespace.

                    # Delete the existing position of the target, and
                    # the _following_ point.
                    fixes.append(LintFix.delete(loc.target))
                    for seg in elem_buff[loc.next_point_idx].segments:
                        fixes.append(LintFix.delete(seg))

                    # We always reinsert before the first point, but respace
                    # the inserted point to ensure it's the right size given
                    # configs.
                    fixes, new_point = ReflowPoint([]).respace_point(
                        elem_buff[loc.prev_code_pt_idx - 1],
                        elem_buff[loc.prev_point_idx + 1],
                        root_segment=self.root_segment,
                        fixes=fixes,
                        anchor_on="before",
                    )
                    fixes.append(
                        LintFix.create_before(
                            elem_buff[loc.prev_code_pt_idx].segments[0],
                            [loc.target],
                        )
                    )

                    elem_buff = (
                        elem_buff[: loc.prev_code_pt_idx]
                        + [new_point]
                        + elem_buff[
                            loc.prev_point_idx + 1 : loc.next_point_idx
                        ]  # the target
                        + elem_buff[loc.prev_code_pt_idx : loc.prev_point_idx + 1]
                        + elem_buff[loc.next_point_idx + 1 :]
                    )

            elif loc.line_position == "alone":
                # If we get here we can assume that the element is currently
                # either leading or trailing and needs to be moved onto it's
                # own line.

                # First handle the following newlines first (easy).
                if not elem_buff[loc.next_nl_idx].num_newlines():
                    reflow_logger.debug("  Found missing newline after in alone case")
                    if prev_point.num_newlines():
                        new_indent = prev_point.get_indent() or ""
                    else:
                        # TODO: This needs to be smarter!
                        new_indent = ""
                    fixes, next_point = next_point.indent_to(
                        new_indent, after=loc.target
                    )
                    # Update the point in the buffer
                    elem_buff[loc.next_point_idx] = next_point

                # Then handle newlines before. (hoisting past comments if needed).
                if not elem_buff[loc.prev_point_idx].num_newlines():
                    reflow_logger.debug("  Found missing newline before in alone case")
                    # NOTE: In the case that there are comments _after_ the
                    # target, they will be moved with it. This might break things
                    # but there isn't an unambiguous way to do this, because we
                    # can't be sure what the comments are referring to.
                    # Given that, we take the simple option.
                    if next_point.num_newlines():
                        new_indent = next_point.get_indent() or ""
                    else:
                        # TODO: This needs to be smarter!
                        new_indent = ""
                    fixes, prev_point = prev_point.indent_to(
                        new_indent, before=loc.target
                    )
                    # Update the point in the buffer
                    elem_buff[loc.prev_point_idx] = prev_point

            else:
                raise NotImplementedError(  # pragma: no cover
                    f"Unexpected line_position config: {loc.line_position}"
                )

        return ReflowSequence(
            elements=elem_buff,
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            embodied_fixes=fixes,
        )
