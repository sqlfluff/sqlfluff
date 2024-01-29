"""Surrogate class for working with Segment collections."""

from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Optional,
    Union,
    overload,
)

from typing_extensions import SupportsIndex  # NOTE: Required for py37

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.utils.functional.raw_file_slices import RawFileSlices

PredicateType = Callable[[BaseSegment], bool]


class Segments(tuple):
    """Encapsulates a sequence of one or more BaseSegments.

    The segments may or may not be contiguous in a parse tree.
    Provides useful operations on a sequence of segments to simplify rule creation.
    """

    def __new__(cls, *segments, templated_file=None):
        """Override new operator."""
        return super(Segments, cls).__new__(cls, segments)

    def __init__(
        self, *_: BaseSegment, templated_file: Optional[TemplatedFile] = None
    ) -> None:
        self.templated_file = templated_file

    def __add__(self, segments_) -> "Segments":
        return Segments(
            *tuple(self).__add__(tuple(segments_)), templated_file=self.templated_file
        )

    def __radd__(self, segments_) -> "Segments":
        return Segments(
            *tuple(segments_).__add__(tuple(self)), templated_file=self.templated_file
        )

    def find(self, segment: Optional[BaseSegment]) -> int:
        """Returns index if found, -1 if not found."""
        try:
            return self.index(segment)
        except ValueError:
            return -1

    def all(self, predicate: Optional[PredicateType] = None) -> bool:
        """Do all the segments match?"""
        for s in self:
            if predicate is not None and not predicate(s):
                return False
        return True

    def any(self, predicate: Optional[PredicateType] = None) -> bool:
        """Do any of the segments match?"""
        for s in self:
            if predicate is None or predicate(s):
                return True
        return False

    def reversed(self) -> "Segments":  # pragma: no cover
        """Return the same segments in reverse order."""
        return Segments(*reversed(self), templated_file=self.templated_file)

    @property
    def raw_slices(self) -> RawFileSlices:
        """Raw slices of the segments, sorted in source file order."""
        if not self.templated_file:
            raise ValueError(
                'Segments.raw_slices: "templated_file" property is required.'
            )
        raw_slices = set()
        for s in self:
            if s.pos_marker is None:
                raise ValueError(
                    "Segments include a positionless segment"
                )  # pragma: no cover
            source_slice = s.pos_marker.source_slice
            raw_slices.update(
                self.templated_file.raw_slices_spanning_source_slice(source_slice)
            )
        return RawFileSlices(
            *sorted(raw_slices, key=lambda slice_: slice_.source_idx),
            templated_file=self.templated_file,
        )

    # TODO:This method isn't used as at 2022-08-10. Consider removing in future.
    @property
    def raw_segments(self) -> "Segments":  # pragma: no cover
        """Get raw segments underlying the segments."""
        raw_segments_list = []
        for s in self:
            raw_segments_list.extend(s.raw_segments)
        return Segments(*raw_segments_list, templated_file=self.templated_file)

    def recursive_crawl_all(self) -> "Segments":  # pragma: no cover
        """Recursively crawl all descendant segments."""
        segments: List[BaseSegment] = []
        for s in self:
            for i in s.recursive_crawl_all():
                segments.append(i)
        return Segments(*segments, templated_file=self.templated_file)

    def recursive_crawl(self, *seg_type: str, recurse_into: bool = True) -> "Segments":
        """Recursively crawl for segments of a given type."""
        segments: List[BaseSegment] = []
        for s in self:
            for i in s.recursive_crawl(*seg_type, recurse_into=recurse_into):
                segments.append(i)
        return Segments(*segments, templated_file=self.templated_file)

    def children(
        self,
        predicate: Optional[PredicateType] = None,
    ) -> "Segments":
        """Returns an object with children of the segments in this object."""
        child_segments: List[BaseSegment] = []
        for s in self:
            for child in s.segments:
                if predicate is None or predicate(child):
                    child_segments.append(child)
        return Segments(*child_segments, templated_file=self.templated_file)

    def first(
        self,
        predicate: Optional[PredicateType] = None,
    ) -> "Segments":
        """Returns the first segment (if any) that satisfies the predicates."""
        for s in self:
            if predicate is None or predicate(s):
                return Segments(s, templated_file=self.templated_file)
        # If no segment satisfies "predicates", return empty Segments.
        return Segments(templated_file=self.templated_file)

    def last(
        self,
        predicate: Optional[PredicateType] = None,
    ) -> "Segments":
        """Returns the last segment (if any) that satisfies the predicates."""
        for s in reversed(self):
            if predicate is None or predicate(s):
                return Segments(s, templated_file=self.templated_file)
        # If no segment satisfies "predicates", return empty Segments.
        return Segments(templated_file=self.templated_file)

    def __iter__(self) -> Iterator[BaseSegment]:  # pragma: no cover
        # Typing understand we are looping BaseSegment
        return super().__iter__()

    @overload
    def __getitem__(self, item: SupportsIndex) -> BaseSegment:
        """Individual "getting" returns a single segment.

        NOTE: Using `SupportsIndex` rather than `int` is to ensure
        type compatibility with the parent `tuple` implementation.
        """

    @overload
    def __getitem__(self, item: slice) -> "Segments":
        """Getting a slice returns another `Segments` object."""

    def __getitem__(
        self, item: Union[SupportsIndex, slice]
    ) -> Union[BaseSegment, "Segments"]:
        result = super().__getitem__(item)
        if isinstance(result, tuple):
            return Segments(*result, templated_file=self.templated_file)
        else:
            return result

    def get(self, index: int = 0, *, default: Any = None) -> Optional[BaseSegment]:
        """Return specified item. Returns default if index out of range."""
        try:
            return self[index]
        except IndexError:
            return default

    def apply(self, fn: Callable[[BaseSegment], Any]) -> List[Any]:
        """Apply function to every item."""
        return [fn(s) for s in self]

    def select(
        self,
        select_if: Optional[PredicateType] = None,
        loop_while: Optional[PredicateType] = None,
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
        return Segments(*buff, templated_file=self.templated_file)

    def iterate_segments(
        self,
        predicate: Optional[PredicateType] = None,
    ) -> Iterable["Segments"]:
        """Loop over each element as a fresh Segments."""
        # Looping over Segments returns BaseEls
        # which is sometime what we want and sometimes not
        for base_el in self:
            if predicate and not predicate(base_el):  # pragma: no cover
                continue
            yield Segments(base_el, templated_file=self.templated_file)
