"""Surrogate class for working with Segment collections."""
from typing import Any, Callable, List, Optional, Sequence, Type, Union

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.core.rules.surrogates.raw_file_slice import RawFileSlices

Predicate = Union[str, Type, Callable[[BaseSegment], bool]]


class Segments(list):
    """Encapsulates a sequence of one or more BaseSegments.

    The segments may or may not be contiguous in a parse tree.
    Provides useful operations on a sequence of segments to simplify rule creation.
    """

    def __new__(cls, templated_file, *segments):
        """Override new operator."""
        return super(Segments, cls).__new__(cls, segments)

    def __init__(self, templated_file: Optional[TemplatedFile], *segments: BaseSegment):
        self.templated_file = templated_file
        self[:] = list(segments)

    def __add__(self, segments) -> "Segments":
        return Segments(self.templated_file, *list(self).__add__(list(segments)))

    def all(self, *predicates: Predicate) -> bool:
        """Do all the segments match?"""
        cp = _CompositePredicate(*predicates)
        return all(cp(s) for s in self)

    def any(self, *predicates: Predicate) -> bool:
        """Do any of the segments match?"""
        cp = _CompositePredicate(*predicates)
        return any(cp(s) for s in self)

    def reversed(self) -> "Segments":
        """Return the same segments in reverse order."""
        return Segments(self.templated_file, *reversed(self))

    @property
    def raw_slices(self) -> RawFileSlices:
        """Raw slices of the segments."""
        if not self.templated_file:  # pragma: no cover
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

    def children(self, *predicates: Predicate) -> "Segments":
        """Returns an object with children of the segments in this object."""
        child_segments: List[BaseSegment] = []
        cp = _CompositePredicate(*predicates)
        for s in self:
            for child in s.segments:
                if cp(child):
                    child_segments.append(child)
        return Segments(self.templated_file, *child_segments)

    def first(self, *predicates) -> Optional["Segments"]:
        """Returns the first segment (if any) that satisfies the predicates."""
        cp = _CompositePredicate(*predicates)
        for s in self:
            if cp(s):
                return Segments(self.templated_file, s)
        # If no segment satisfies "predicates", return "None".
        return None

    def last(self, *predicates) -> Optional["Segments"]:
        """Returns the last segment (if any) that satisfies the predicates."""
        cp = _CompositePredicate(*predicates)
        for s in reversed(self):
            if cp(s):
                return Segments(self.templated_file, s)
        # If no segment satisfies "predicates", return "None".
        return None

    def apply(self, fn: Callable[[BaseSegment], Any]) -> List[Any]:
        """Apply function to every item."""
        return [fn(s) for s in self]

    def select(
        self,
        select_if: Optional[Sequence[Predicate]] = None,
        loop_while: Optional[Sequence[Predicate]] = None,
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
        cp_select_if = None
        if select_if:
            cp_select_if = _CompositePredicate(*select_if)
        cp_loop_while = None
        if loop_while:
            cp_loop_while = _CompositePredicate(*loop_while)
        for seg in self[start_index + 1 : stop_index]:
            if cp_loop_while and not cp_loop_while(seg):
                break
            if not cp_select_if or cp_select_if(seg):
                buff.append(seg)
        return Segments(self.templated_file, *buff)


class _CompositePredicate:
    def __init__(self, *predicates: Predicate):
        self.type_names: List[str] = []
        self.other = []
        for p in predicates:
            if isinstance(p, str):
                self.type_names.append(p)
            else:
                self.other.append(p)

    def __call__(self, segment: BaseSegment) -> bool:
        if self.type_names and not segment.is_type(*self.type_names):
            return False

        for p in self.other:
            if isinstance(p, type):
                # Check segment class
                if not isinstance(segment, p):  # pragma: no cover
                    return False
            elif not p(segment):  # Arbitrary function
                return False
        return True
