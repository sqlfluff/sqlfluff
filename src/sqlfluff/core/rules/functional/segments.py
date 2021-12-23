"""Surrogate class for working with Segment collections."""
from typing import Any, Callable, List, Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.core.rules.surrogates.raw_file_slice import RawFileSlices


class Segments(tuple):
    """Encapsulates a sequence of one or more BaseSegments.

    The segments may or may not be contiguous in a parse tree.
    Provides useful operations on a sequence of segments to simplify rule creation.
    """

    def __new__(cls, templated_file, *segments):
        """Override new operator."""
        return super(Segments, cls).__new__(cls, segments)

    def __init__(self, templated_file: Optional[TemplatedFile], *_: BaseSegment):
        self.templated_file = templated_file

    def __add__(self, segments_) -> "Segments":
        return Segments(self.templated_file, *tuple(self).__add__(tuple(segments_)))

    def __radd__(self, segments_) -> "Segments":
        return Segments(self.templated_file, *tuple(segments_).__add__(tuple(self)))

    def all(self, predicate: Optional[Callable[[BaseSegment], bool]] = None) -> bool:
        """Do all the segments match?"""
        for s in self:
            if predicate is not None and not predicate(s):
                return False
        return True

    def any(self, predicate: Optional[Callable[[BaseSegment], bool]] = None) -> bool:
        """Do any of the segments match?"""
        for s in self:
            if predicate is None or predicate(s):
                return True
        return False

    def reversed(self) -> "Segments":  # pragma: no cover
        """Return the same segments in reverse order."""
        return Segments(self.templated_file, *reversed(self))

    @property
    def raw_slices(self) -> RawFileSlices:
        """Raw slices of the segments."""
        if not self.templated_file:
            raise ValueError(
                'Segments.raw_slices: "templated_file" property is required.'
            )
        raw_slices = set()
        for s in self:
            source_slice = s.pos_marker.source_slice
            raw_slices.update(
                self.templated_file.raw_slices_spanning_source_slice(source_slice)
            )
        return RawFileSlices(self.templated_file, *raw_slices)

    def children(
        self, predicate: Optional[Callable[[BaseSegment], bool]] = None
    ) -> "Segments":
        """Returns an object with children of the segments in this object."""
        child_segments: List[BaseSegment] = []
        for s in self:
            for child in s.segments:
                if predicate is None or predicate(child):
                    child_segments.append(child)
        return Segments(self.templated_file, *child_segments)

    def first(
        self, predicate: Optional[Callable[[BaseSegment], bool]] = None
    ) -> Optional["Segments"]:
        """Returns the first segment (if any) that satisfies the predicates."""
        for s in self:
            if predicate is None or predicate(s):
                return Segments(self.templated_file, s)
        # If no segment satisfies "predicates", return "None".
        return None

    def last(
        self, predicate: Optional[Callable[[BaseSegment], bool]] = None
    ) -> Optional["Segments"]:
        """Returns the last segment (if any) that satisfies the predicates."""
        for s in reversed(self):
            if predicate is None or predicate(s):
                return Segments(self.templated_file, s)
        # If no segment satisfies "predicates", return "None".
        return None

    def apply(self, fn: Callable[[BaseSegment], Any]) -> List[Any]:
        """Apply function to every item."""
        return [fn(s) for s in self]

    def select(
        self,
        select_if: Optional[Callable[[BaseSegment], bool]] = None,
        loop_while: Optional[Callable[[BaseSegment], bool]] = None,
        start_seg: Optional[BaseSegment] = None,
        stop_seg: Optional[BaseSegment] = None,
    ) -> "Segments":
        """Retrieve range/subset.

        NOTE: Iterates the segments BETWEEN start_seg and stop_seg, i.e. those
        segments are not included in the loop.
        """
        start_index = self.index(start_seg) if start_seg else -1
        stop_index = self.index(stop_seg) if stop_seg else len(self)
        buff = []
        for seg in self[start_index + 1 : stop_index]:
            if loop_while is not None and not loop_while(seg):
                break
            if select_if is None or select_if(seg):
                buff.append(seg)
        return Segments(self.templated_file, *buff)
