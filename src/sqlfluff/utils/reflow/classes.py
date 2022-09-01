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


# Until we have a proper structure this will work.
# TODO: Migrate this to the config file.
SPACING_CONFIG = {
    "start_bracket": {"after": "close"},
    "end_bracket": {"before": "close"},
    "comma": {"before": "close"},
    "statement_terminator": {"before": "close"},
    "casting_operator": {"before": "close", "after": "close"},
}
SPACING_CONFIG_TYPES = set(SPACING_CONFIG.keys())


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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
        configured_types = self.class_types.intersection(SPACING_CONFIG_TYPES)
        # We use a for loop here so that all matched configs are applied
        # although there isn't a formal precedence here. This could lead
        # to bugs when it gets complicated - but ok for now.
        # In most cases there will only be one...so no problem.
        for seg_type in configured_types:
            # We're using object.__setattr__ because ReflowBlock is frozen.
            object.__setattr__(
                self, "after", SPACING_CONFIG[seg_type].get("after", self.after)
            )
            object.__setattr__(
                self, "before", SPACING_CONFIG[seg_type].get("before", self.before)
            )


@dataclass(frozen=True)
class ReflowPoint(_ReflowElement):
    """Class for keeping track of editable elements in reflow.

    It holds segments which can be changed during a reflow operation
    such as whitespace and newlines.

    It holds no configuration and is influenced by the blocks either
    side.
    """

    def respace(
        self,
        prev_block: Optional[ReflowBlock] = None,
        next_block: Optional[ReflowBlock] = None,
        fixes: Optional[List[LintFix]] = None,
    ) -> Tuple[List[LintFix], "ReflowPoint"]:
        """Respace a point based on given constraints.

        NB: This effectively includes trailing whitespace fixes.

        Deletion and edit fixes are generated immediately, but creations
        are paused to the end and done in bulk so as not to generate conflicts.
        """
        new_fixes = []
        last_whitespace: List[RawSegment] = []
        # The buffer is used to create the new reflow point to return
        segment_buffer = list(self.segments)
        edited = False

        reflow_logger.debug("Respacing: %s", self)
        for idx, seg in enumerate(self.segments):
            # If it's whitespace, store it.
            if seg.is_type("whitespace"):
                last_whitespace.append(seg)
            # If it's a newline, check if we've just passed whitespace
            elif seg.is_type("newline", "end_of_file"):
                # If we have, remove it as trailing whitespace.
                # Both from the buffer and create a fix.
                if last_whitespace:
                    for ws in last_whitespace:
                        segment_buffer.remove(ws)
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
                segment_buffer.remove(ws)
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
                        # Not just unequal. Must be actively _before_.
                        # NOTE: Based on working locations
                        and prev_seg.get_end_loc() < ws_seg.get_start_loc()
                    ):
                        reflow_logger.debug(
                            "    Removing non-contiguous whitespace post removal."
                        )
                        segment_buffer.remove(ws_seg)
                        new_fixes.append(LintFix("delete", ws_seg))

        # Is this an inline case? (i.e. no newline)
        else:
            pre_constraint = prev_block.after if prev_block else "single"
            post_constraint = next_block.before if next_block else "single"
            reflow_logger.debug(
                "    Inline case. Constraints: %s <-> %s.",
                pre_constraint,
                post_constraint,
            )

            # Do we at least have _some_ whitespace?
            if last_whitespace:
                # We do - is it the right size?

                # Do we have either side set to "close"
                if "close" in [pre_constraint, post_constraint]:
                    # In this instance - no whitespace is correct
                    raise NotImplementedError(f"CLOSE CASE! {self.segments}")
                # Handle the default case
                elif pre_constraint == post_constraint == "single":
                    if last_whitespace[0].raw != " ":
                        new_seg = last_whitespace[0].edit(" ")
                        seg_idx = segment_buffer.index(last_whitespace[0])
                        new_fixes.append(
                            LintFix(
                                "replace",
                                anchor=last_whitespace[0],
                                edit=[new_seg],
                            )
                        )
                        segment_buffer[seg_idx] = new_seg
                else:
                    raise NotImplementedError(
                        f"Unexpected Constraints: {pre_constraint}, {post_constraint}"
                    )
            else:
                # No. Should we insert some?

                # Do we have either side set to "close"
                if "close" in [pre_constraint, post_constraint]:
                    # In this instance - no whitespace is correct
                    pass
                # Handle the default case
                elif pre_constraint == post_constraint == "single":
                    # Insert a single whitespace.
                    reflow_logger.debug("    Inserting Single Whitespace.")
                    # Add it to the buffer first (the easy bit)
                    segment_buffer = [WhitespaceSegment()]

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
                        reflow_logger.debug(
                            "    Detected existing fix %s", existing_fix
                        )
                        if not fixes:  # pragma: no cover
                            raise ValueError(
                                "Fixes detected, but none passed to .respace(). "
                                "This will cause conflicts."
                            )
                        # Find the fix
                        for fix in fixes:
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
                        edited = True
                    else:
                        reflow_logger.debug(
                            "    Not Detected existing fix. Creating new"
                        )
                        if prev_block:
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

        # Only log if we actually made a change.
        if new_fixes or edited:
            reflow_logger.debug(
                "    Fixes. Old & Changed: %s. New: %s", fixes, new_fixes
            )
        return (fixes or []) + new_fixes, ReflowPoint(
            segment_buffer, root_segment=self.root_segment
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
        elements: Sequence[_ReflowElement],
        root_segment: BaseSegment,
        embodied_fixes: Optional[List[LintFix]] = None,
    ):
        # First validate integrity
        self._validate_reflow_sequence(elements, root_segment)
        # Then save
        self.elements = elements
        self.root_segment = root_segment
        # This keeps track of fixes generated in the chaining process.
        # Alternatively pictured: This is the list of fixes required
        # to generate this sequence. We can build on this as we edit
        # the sequence.
        self.embodied_fixes: List[LintFix] = embodied_fixes or []

    def get_fixes(self):
        """Get the current fix buffer."""
        return self.embodied_fixes

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

    @staticmethod
    def _elements_from_raw_segments(
        segments: Sequence[RawSegment], root_segment: BaseSegment
    ) -> Sequence[_ReflowElement]:
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

            elem_buff.append(SeqClass(segments=seg_buff, root_segment=root_segment))
            # Then check whether this a second block and whether
            # we need to add empty point in between.
            if NextClass is ReflowBlock and SeqClass is ReflowBlock:
                elem_buff.append(ReflowPoint(segments=[], root_segment=root_segment))
            seg_buff = [seg]
            SeqClass = NextClass

        if seg_buff and SeqClass:
            elem_buff.append(SeqClass(segments=seg_buff, root_segment=root_segment))

        return elem_buff

    @classmethod
    def from_raw_segments(
        cls, segments: Sequence[RawSegment], root_segment: BaseSegment
    ):
        """Construct a ReflowSequence from a sequence of raw segments.

        Aimed to be the basic constructor, which other more specific
        ones may fall back to.
        """
        return cls(
            elements=cls._elements_from_raw_segments(segments, root_segment),
            root_segment=root_segment,
        )

    @classmethod
    def from_root(cls, root_segment: BaseSegment):
        """Generate a sequence from a root segment."""
        return cls.from_raw_segments(root_segment.raw_segments, root_segment)

    @classmethod
    def from_around_target(
        cls,
        target_segment: BaseSegment,
        root_segment: BaseSegment,
        sides: str = "both",
    ):
        """Generate a sequence around a target.

        Args:
            target_segment (:obj:`RawSegment`): The segment to center
                around when considering the sequence to construct.
            root_segment (:obj:`BaseSegment`): The relevant root
                segment (usually the base :obj:`FileSegment`).
            sides (:obj:`str`): Limit the reflow sequence to just one
                side of the target. Default is two sided ("both"), but
                set to "before" or "after" to limit to either side.


        To evaluate reflow around a specific target, we need
        need to generate a sequence which goes for the preceding
        raw to the following raw.
        i.e. block - point - block - point - block
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
            while pre_idx - 1 > 0 and all_raws[pre_idx].is_type(
                "whitespace", "newline", "indent"
            ):
                pre_idx -= 1
        if sides in ("both", "after"):
            while post_idx < len(all_raws) and all_raws[post_idx].is_type(
                "whitespace", "newline", "indent"
            ):
                post_idx += 1
            # Capture one more after the whitespace.
            post_idx += 1
        segments = all_raws[pre_idx:post_idx]
        reflow_logger.debug(
            "Generating ReflowSequence.from_around_target(). idx: %s. "
            "slice: %s:%s. segments: %s",
            initial_idx,
            pre_idx,
            post_idx,
            segments,
        )
        # Include the final index so +1
        return cls.from_raw_segments(segments, root_segment)

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
            root_segment=self.root_segment,
        )
        return ReflowSequence(
            elements=list(self.elements[: removal_idx - 1])
            + [merged_point]
            + list(self.elements[removal_idx + 2 :]),
            root_segment=self.root_segment,
            # Generate the fix to do the removal.
            embodied_fixes=[LintFix.delete(target)],
        )

    def insert(
        self, insertion: RawSegment, target: RawSegment, pos="before"
    ) -> "ReflowSequence":
        """Returns a new reflow sequence with the new element inserted.

        Insertion is always relative to an existing element. Either before
        or after it as specified by `pos`.
        """
        assert pos in ("before", "after")
        target_idx = self._find_element_idx_with(target)
        # Are we inserting something whitespacey...
        # NOTE: I'm not sure we will _ever_ use this next section. Once
        # more rules are using respace we should evaluate whether to keep
        # this. We might decide that it will never exist.
        if insertion.is_type("whitespace", "indent", "newline"):  # pragma: no cover
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
                raise NotImplementedError(  # pragma: no cover
                    "Can't insert relative to whitespace for now."
                )
            elif pos == "before":
                return ReflowSequence(
                    elements=list(self.elements[:target_idx])
                    + [new_block, ReflowPoint([], root_segment=self.root_segment)]
                    + list(self.elements[target_idx:]),
                    root_segment=self.root_segment,
                    # Generate the fix to do the removal.
                    embodied_fixes=[LintFix.create_before(target, [insertion])],
                )
            elif pos == "after":  # pragma: no cover
                # TODO: This doesn't get coverage - should it even exist?
                # Re-evaluate whether this code path is ever taken once more rules use
                # this.
                return ReflowSequence(
                    elements=list(self.elements[: target_idx + 1])
                    + [ReflowPoint([], root_segment=self.root_segment), new_block]
                    + list(self.elements[target_idx + 1 :]),
                    root_segment=self.root_segment,
                    # Generate the fix to do the removal.
                    embodied_fixes=[LintFix.create_after(target, [insertion])],
                )
            raise ValueError(f"Unexpected value for ReflowSequence.insert(pos): {pos}")

    def replace(
        self, target: BaseSegment, edit: Sequence[BaseSegment]
    ) -> "ReflowSequence":
        """Returns a new reflow sequence elements replaced."""
        replace_fix = LintFix.replace(target, edit)

        target_raws = target.raw_segments
        assert target_raws

        edit_raws = list(chain.from_iterable(seg.raw_segments for seg in edit))

        # It's much easier to just totally reconstruct the sequence rather
        # than do surgery on the elements.
        current_raws = list(
            chain.from_iterable(elem.segments for elem in self.elements)
        )
        start_idx = current_raws.index(target_raws[0])
        last_idx = current_raws.index(target_raws[-1])

        return ReflowSequence(
            self._elements_from_raw_segments(
                current_raws[:start_idx] + edit_raws + current_raws[last_idx + 1 :],
                root_segment=self.root_segment,
            ),
            root_segment=self.root_segment,
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

    def respace(self) -> "ReflowSequence":
        """Respace a sequence.

        This resets spacing in a ReflowSequence. Note, it relies on the
        embodied fixes being correct so that we can build on them.
        """
        # Use the embodied fixes as a starting point.
        fixes = self.embodied_fixes or []
        new_elements: List[_ReflowElement] = []
        for point, pre, post in self._iter_points_with_constraints():
            # Pass through the fixes because they may get mutated
            # TODO: This feels a bit gross - can we do better?
            fixes, new_point = point.respace(
                prev_block=pre, next_block=post, fixes=fixes
            )
            if pre and (not new_elements or new_elements[-1] != pre):
                new_elements.append(pre)
            new_elements.append(new_point)
            if post:
                new_elements.append(post)
        return ReflowSequence(
            elements=new_elements,
            root_segment=self.root_segment,
            # Generate the fix to do the removal.
            embodied_fixes=fixes,
        )

    def trailing_whitespace_fixes(self) -> List[LintFix]:
        """Fix any trailing whitespace detected."""
        fixes = []
        for elem in self.elements:
            if isinstance(elem, ReflowPoint) and any(
                seg.is_type("newline", "end_of_file") for seg in elem.segments
            ):
                new_fixes, _ = elem.respace()
                fixes.extend(new_fixes)
        return fixes
