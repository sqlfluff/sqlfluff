"""Dataclasses for reflow work."""


from itertools import chain
import logging
from dataclasses import dataclass
from typing import List, Sequence, Union, Type

from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.rules.base import LintFix


reflow_logger = logging.getLogger("sqlfluff.utils.reflow")


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

            reflow_logger.debug(
                "    Evaluating %s. NextClass: %s, SeqClass: %s",
                seg,
                NextClass.__name__,
                SeqClass.__name__ if SeqClass else None,
            )
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

    def trailing_whitespace_fixes(self) -> List[LintFix]:
        """Fix any trailing whitespace detected."""
        fixes = []
        for elem in self.elements:
            if isinstance(elem, ReflowPoint):
                fixes.extend(elem.trailing_whitespace_fixes())
        return fixes
