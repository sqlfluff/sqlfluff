"""Dataclasses for reflow work."""


from itertools import chain
import logging
from dataclasses import dataclass
from typing import Iterator, List, Optional, Sequence, Tuple, Union, Type, cast

from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.parser.segments.raw import WhitespaceSegment
from sqlfluff.core.rules.base import LintFix


# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


@dataclass
class _ReflowElement:
    """Base reflow element class."""

    segments: Sequence[RawSegment]
    root_segment: BaseSegment

    @property
    def class_types(self):
        """The set of contained class types.

        Parallel to BaseSegment.class_types
        """
        return set(chain.from_iterable(seg.class_types for seg in self.segments))


@dataclass
class ReflowBlock(_ReflowElement):
    """Class for keeping track of elements to reflow.

    It holds segments to reflow and also exposes configuration
    around how they are expected to reflow around others.

    The attributes exposed are designed to be "post configuration"
    i.e. they should reflect configuration appropriately.

    NOTE: These are the smallest unit of "work" within
    the reflow methods, and may contain meta segments.
    """

    # Options for spacing rules are:
    # - single: the default (one single space)
    # - close: no whitespace
    before: str = "single"
    after: str = "single"

    def __post_init__(self):
        """Infer spacing behaviour post-init."""
        # NOTE: This should probably be configured differently in
        # future, but this works initially. Delegating spacing
        # configuration to the dialect or an explicit config
        # are the two most likely options.
        # TODO: This is not covered in tests yet, it's prep for later.
        if {"start_bracket"} in self.class_types:
            self.after = "close"  # pragma: no cover
        elif {"end_bracket"} in self.class_types:
            self.before = "close"  # pragma: no cover


@dataclass
class ReflowPoint(_ReflowElement):
    """Class for keeping track of editable elements in reflow.

    It holds segments which can be changed during a reflow operation
    such as whitespace and newlines.

    It holds no configuration and is influenced by the blocks either
    side.
    """

    def respace(
        self,
        after: Optional[ReflowBlock] = None,
        before: Optional[ReflowBlock] = None,
        fixes: Optional[List[LintFix]] = None,
    ) -> List[LintFix]:
        """Respace a point based on given constraints.

        NB: This effectively includes trailing whitespace fixes.

        Deletion and edit fixes are generated immediately, but creations
        are paused to the end and done in bulk so as not to generate conflicts.
        """
        new_fixes = []
        last_whitespace: List[RawSegment] = []

        reflow_logger.debug("Respacing: %s", self)
        for idx, seg in enumerate(self.segments):
            # If it's whitespace, store it.
            if seg.is_type("whitespace"):
                last_whitespace.append(seg)
            # If it's a newline, check if we've just passed whitespace
            elif seg.is_type("newline", "end_of_file"):
                # If we have, remove it as trailing whitespace
                if last_whitespace:
                    for ws in last_whitespace:
                        new_fixes.append(LintFix("delete", ws))
                    reflow_logger.debug("    Removing trailing whitespace.")
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
                new_fixes.append(LintFix("delete", ws))

        # Is there a newline?
        if self.class_types.intersection({"newline", "end_of_file"}):
            # Most of this section should be handled as _Indentation_.
            # BUT: There is one case we should handle here.
            # If we find that the last whitespace has a newline
            # before it, and the position markers imply there was
            # a removal between them. Remove the whitespace.
            # This ensures a consistent indent.
            # TODO: Check this doesn't duplicate indentation code
            # once written.
            if len(last_whitespace) == 1:
                ws_seg = last_whitespace[0]
                ws_idx = self.segments.index(ws_seg)
                if ws_idx > 0:
                    prev_seg = self.segments[ws_idx - 1]
                    if (
                        prev_seg.is_type("newline")
                        and prev_seg.pos_marker.end_point_marker()
                        != ws_seg.pos_marker.start_point_marker()
                    ):
                        reflow_logger.debug(
                            "    Removing non-contiguous whitespace " "post removal."
                        )
                        new_fixes.append(LintFix("delete", ws_seg))

        # Is this an inline case? (i.e. no newline)
        else:
            # Do we at least have _some_ whitespace?
            if last_whitespace:
                # We do - is it the right size?
                if (not after or after.after == "single") and (
                    not before or before.before == "single"
                ):
                    if last_whitespace[0].raw != " ":
                        new_fixes.append(
                            LintFix(
                                "edit",
                                anchor=last_whitespace[0],
                                edit=last_whitespace[0].edit(" "),
                            )
                        )
                else:
                    raise NotImplementedError(
                        "Not set up to handle non-single whitespace rules."
                    )
            else:
                # No. Should we insert some?
                if (not after or after.after == "single") and (
                    not before or before.before == "single"
                ):
                    # Insert a single whitespace.

                    # So special handling here. If segments either side
                    # already exist then we don't care which we anchor on
                    # but if one is already an insertion (as shown by a lack)
                    # of pos_marker, then we should piggy back on that pre-existing
                    # fix.
                    existing_fix = None
                    insertion = None
                    if after and not after.segments[-1].pos_marker:
                        existing_fix = "after"
                        insertion = after.segments[-1]
                    elif before and not before.segments[0].pos_marker:
                        existing_fix = "before"
                        insertion = before.segments[0]

                    if existing_fix:
                        reflow_logger.debug("Detected existing fix %s", existing_fix)
                        if not fixes:
                            raise ValueError(
                                "Fixes detected, but none passed to .respace(). "
                                "This will cause conflicts."
                            )
                        # Find the fix
                        for fix in fixes:
                            # Does it contain the insertion?
                            # TODO: This feels ugly - why is eq for BaseSegment defined
                            # so differently?!!?!???!? Shouldn't it all use uuids?
                            if (
                                insertion
                                and fix.edit
                                and insertion.uuid in [elem.uuid for elem in fix.edit]
                            ):
                                break
                        else:
                            reflow_logger.warning("Fixes %s", fixes)
                            raise ValueError(f"Couldn't find insertion for {insertion}")
                        # Mutate the existing fix
                        assert fix
                        assert (
                            fix.edit
                        )  # It's going to be an edit if we've picked it up.
                        if existing_fix == "before":
                            fix.edit = [
                                cast(BaseSegment, WhitespaceSegment())
                            ] + fix.edit
                        elif existing_fix == "after":
                            fix.edit = fix.edit + [
                                cast(BaseSegment, WhitespaceSegment())
                            ]
                    else:
                        reflow_logger.debug("Not Detected existing fix. Creating new")
                        if after:
                            new_fixes.append(
                                LintFix(
                                    "create_after",
                                    anchor=after.segments[-1],
                                    edit=[WhitespaceSegment()],
                                )
                            )
                        elif before:
                            new_fixes.append(
                                LintFix(
                                    "create_before",
                                    anchor=before.segments[0],
                                    edit=[WhitespaceSegment()],
                                )
                            )
                        else:
                            NotImplementedError(
                                "Not set up to handle a missing _after_ and _before_."
                            )
                else:
                    raise NotImplementedError(
                        "Not set up to handle non-single whitespace rules."
                    )

        reflow_logger.debug("Old and Modified fixes: %s", fixes)
        reflow_logger.debug("New fixes: %s", new_fixes)
        return (fixes or []) + new_fixes

    def trailing_whitespace_fixes(self) -> List[LintFix]:
        """Fix any trailing whitespace detected.

        Trailing whitespace is unique in that it can be detected
        solely within the reflow point. It is any whitespace
        preceeding a newline.
        """
        # NOTE: We will need an end_of_file marker to do file ends.
        reflow_logger.debug("TW: Checking %s", self)
        if not self.class_types.intersection({"newline", "end_of_file"}):
            return []
        fixes = []
        for idx, seg in enumerate(self.segments):
            if not (
                seg.is_type("newline", "end_of_file")
                and idx > 0
                and self.segments[idx - 1].is_type("whitespace")
            ):
                continue
            # NOTE: If there's a loop marker in the way, then this
            # won't trigger. That way we avoid flagging in templated
            # use cases where it's actually a loop.
            fixes.append(LintFix("delete", self.segments[idx - 1]))
            reflow_logger.debug("    !! TW: TRAILING WHITESPACE")
        return fixes


@dataclass
class ReflowSequence:
    """Class for keeping track of elements in a reflow operation.

    It is assumed that there will be alternating blocks and points
    (even if some points have no segments). This is validated on
    construction.

    We assume points on each end because this is the case with a file.
    """

    elements: Sequence[_ReflowElement]
    root_segment: BaseSegment

    def __post_init__(self):
        """Validate integrity."""
        self._validate_reflow_sequence(self.elements, self.root_segment)

    @staticmethod
    def _validate_reflow_sequence(
        elements: Sequence[_ReflowElement], root_segment: BaseSegment
    ):
        assert elements, "ReflowSequence has empty elements."
        # Check root segment is shared
        assert all(
            elem.root_segment is root_segment for elem in elements
        ), "ReflowSequence has inconsistent root."
        # Check first and last
        try:
            if isinstance(elements[0], ReflowPoint):
                # Check odds are all points
                assert all(
                    isinstance(elem, ReflowPoint) for elem in elements[::2]
                ), "Not all odd elements are ReflowPoint"
                # Check evens are all blocks
                assert all(
                    isinstance(elem, ReflowBlock) for elem in elements[1::2]
                ), "Not all even elements are ReflowBlock"
            else:
                # Check odds are all points
                assert all(
                    isinstance(elem, ReflowBlock) for elem in elements[::2]
                ), "Not all odd elements are ReflowBlock"
                # Check evens are all blocks
                assert all(
                    isinstance(elem, ReflowPoint) for elem in elements[1::2]
                ), "Not all even elements are ReflowPoint"
        except AssertionError as err:  # pragma: no cover
            for elem in elements:
                reflow_logger.error("   - %s", elem)
            reflow_logger.exception("Assertion check on ReflowSequence failed.")
            raise err

    @classmethod
    def from_raw_segments(
        cls, segments: Sequence[RawSegment], root_segment: BaseSegment
    ):
        """Construct a ReflowSequence from a sequence of raw segments.

        Aimed to be the basic constructor, which other more specific
        ones may fall back to.
        """
        elem_buff = []
        seg_buff: List[RawSegment] = []
        SeqClass: Union[None, Type[ReflowBlock], Type[ReflowPoint]] = None
        for seg in segments:
            NextClass: Union[Type[ReflowBlock], Type[ReflowPoint]] = (
                ReflowPoint
                if seg.is_type("whitespace", "newline", "end_of_file", "indent")
                else ReflowBlock
            )
            # NOTE: Can indents be in a reflow block? I assume not.
            # Placeholders certainly not because they also get indented.

            if (
                # Extend the buffer if we're the first segment.
                not SeqClass
                # Extend the buffer if we're still in a spacing section.
                or (SeqClass is ReflowPoint and NextClass is ReflowPoint)
            ):
                seg_buff.append(seg)
                SeqClass = NextClass
                continue

            reflow_logger.debug(
                "Appending %s with %s elements: %s",
                SeqClass.__name__,
                len(seg_buff),
                seg_buff,
            )
            elem_buff.append(SeqClass(segments=seg_buff, root_segment=root_segment))
            # Then check whether this a second block and whether
            # we need to add empty point in between.
            if NextClass is ReflowBlock and SeqClass is ReflowBlock:
                reflow_logger.debug("Appending Empty ReflowPoint")
                elem_buff.append(ReflowPoint(segments=[], root_segment=root_segment))
            seg_buff = [seg]
            SeqClass = NextClass

        if seg_buff and SeqClass:
            reflow_logger.debug(
                "Appending %s with %s elements: %s",
                SeqClass.__name__,
                len(seg_buff),
                seg_buff,
            )
            elem_buff.append(SeqClass(segments=seg_buff, root_segment=root_segment))

        return cls(elements=elem_buff, root_segment=root_segment)

    @classmethod
    def from_root(cls, root_segment: BaseSegment):
        """Generate a sequence from a root segment."""
        return cls.from_raw_segments(root_segment.raw_segments, root_segment)

    @classmethod
    def from_around_target(cls, target_segment: RawSegment, root_segment: BaseSegment):
        """Generate a sequence around a target.

        To evaluate reflow around a specific target, we need
        need to generate a sequence which goes for the preceeding
        raw to the following raw.
        i.e. block - point - block - point - block
        (where the central block is the target).
        """
        # There's probably a more efficient way than immediately
        # materialising the raw_segments for the whole root, but
        # it works. Optimise later.
        all_raws = root_segment.raw_segments
        idx = all_raws.index(target_segment)
        pre_idx = idx - 1
        post_idx = idx + 1
        while pre_idx > 0 and all_raws[pre_idx].is_type(
            "whitespace", "newline", "indent"
        ):
            pre_idx -= 1
        while post_idx < len(all_raws) and all_raws[post_idx].is_type(
            "whitespace", "newline", "indent"
        ):
            # TODO: This isn't covered with tests yet.
            post_idx += 1  # pragma: no cover
        segments = all_raws[pre_idx : post_idx + 1]
        reflow_logger.debug(
            "Generating ReflowSequence.from_around_target(). idx: %s. "
            "slice: %s:%s. segments: %s",
            idx,
            pre_idx,
            post_idx,
            segments,
        )
        # Include the final index so +1
        return cls.from_raw_segments(segments, root_segment)

    def _find_element_idx_with(self, target: BaseSegment) -> int:
        for idx, elem in enumerate(self.elements):
            if target in elem.segments:
                return idx
        raise ValueError(f"Target [{target}] not found in ReflowSequence.")

    def without(self, target: BaseSegment) -> "ReflowSequence":
        """Returns a new reflow sequence without the specified segment.

        It's important to note that this doesn't itself remove the target
        from the file. This just allows us to simulate a sequence without it
        and work out what additional whitespace changes would be required
        if we were to remove it.
        """
        removal_idx = self._find_element_idx_with(target)
        if removal_idx == 0 or removal_idx == len(self.elements) - 1:
            raise NotImplementedError(
                "Unexpected removal at one end of a ReflowSequence."
            )
        if isinstance(self.elements[removal_idx], ReflowPoint):
            raise NotImplementedError(
                "Not expected removal of whitespace in ReflowSequence."
            )
        merged_point = ReflowPoint(
            segments=list(self.elements[removal_idx - 1].segments)
            + list(self.elements[removal_idx + 1].segments),
            root_segment=self.root_segment,
        )
        return ReflowSequence(
            elements=list(self.elements[: removal_idx - 1])
            + [merged_point]
            + list(self.elements[removal_idx + 2 :]),
            root_segment=self.root_segment,
        )

    def insert(self, insertion: RawSegment, target: RawSegment, pos="before"):
        """Returns a new reflow sequence with the new element inserted.

        Insertion is always relative to an existing element. Either before
        or after it as specified by `pos`.
        """
        assert pos in ("before", "after")
        target_idx = self._find_element_idx_with(target)
        # Are we inserting something whitespacey...
        if insertion.is_type("whitespace", "indent", "newline"):
            # ... into a point?
            if isinstance(self.elements[target_idx], ReflowPoint):
                # This is the easy case where we just append the new segment
                # into the existing one.
                point_idx = target_idx
            # ... around a block?
            else:
                # We're inserting whitespace around a block
                point_idx = target_idx + (1 if pos == "before" else -1)
            new_segments = (
                ([insertion] if pos == "before" else [])
                + list(self.elements[point_idx].segments)
                + ([insertion] if pos == "after" else [])
            )
            new_point = ReflowPoint(
                segments=new_segments, root_segment=self.root_segment
            )
            return ReflowSequence(
                elements=list(self.elements[:point_idx])
                + [new_point]
                + list(self.elements[point_idx + 1 :]),
                root_segment=self.root_segment,
            )
        else:
            # We're inserting something blocky. That means a new block AND a new point.
            # It's possible we try to _split_ a point by targetting a whitespace element
            # inside a larger point. For now this isn't supported.
            new_block = ReflowBlock(
                segments=[insertion], root_segment=self.root_segment
            )
            if isinstance(self.elements[target_idx], ReflowPoint):
                raise NotImplementedError(
                    "Can't insert relative to whitespace for now."
                )
            elif pos == "before":
                return ReflowSequence(
                    elements=list(self.elements[:target_idx])
                    + [new_block, ReflowPoint([], root_segment=self.root_segment)]
                    + list(self.elements[target_idx:]),
                    root_segment=self.root_segment,
                )
            elif pos == "after":
                return ReflowSequence(
                    elements=list(self.elements[: target_idx + 1])
                    + [ReflowPoint([], root_segment=self.root_segment), new_block]
                    + list(self.elements[target_idx + 1 :]),
                    root_segment=self.root_segment,
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
                if idx < len(self.elements) - 2:
                    post = cast(ReflowBlock, self.elements[idx + 1])
                yield elem, pre, post

    def respace(self, fixes: Optional[List[LintFix]] = None) -> List[LintFix]:
        """Respace a sequence.

        This resets spacing in a ReflowSequence.

        Args:
            fixes (:obj:`list` of :obj:`BaseSegment`, optional): Optionally
                provide a list of existing fixes to be applied so that we can
                merge additional changes into those existing fixes and not
                trigger issues with multiple fixes aimed at the same segment.
        """
        fixes = fixes or []
        for point, pre, post in self._iter_points_with_constraints():
            # Pass through the fixes because they may get mutated
            # TODO: This feels a bit gross - can we do better?
            fixes = point.respace(after=pre, before=post, fixes=fixes)
        return fixes

    def trailing_whitespace_fixes(self) -> List[LintFix]:
        """Fix any trailing whitespace detected."""
        fixes = []
        for elem in self.elements:
            if isinstance(elem, ReflowPoint) and any(seg.is_type('newline') for seg in elem.segments):
                fixes.extend(elem.respace())
        return fixes
