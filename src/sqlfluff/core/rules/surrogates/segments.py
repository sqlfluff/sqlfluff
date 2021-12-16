"""Surrogate class for working with Segment collections."""
from typing import Callable, List, Optional, Sequence, Type, TypeVar

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.base import LintFix
from sqlfluff.core.templaters.base import TemplatedFile
from sqlfluff.core.rules.surrogates.raw_file_slice import RawFileSlices

Predicate = TypeVar("Predicate", str, Type, Callable[[BaseSegment], bool])


class Segments:
    """Encapsulates a sequence of one or more BaseSegments.

    The segments may or may not be contiguous in a parse tree.
    Provides useful operations on a sequence of segments to simplify rule creation.
    """

    def __init__(self, templated_file: Optional[TemplatedFile], *segments: BaseSegment):
        self.templated_file = templated_file
        self.segments = segments

    def all(self, *predicates: Predicate) -> bool:
        """Do all the segments match?"""
        cp = _CompositePredicate(*predicates)
        return all(cp(s) for s in self.segments)

    def any(self, *predicates: Predicate) -> bool:  # pragma: no cover
        """Do any of the segments match?"""
        cp = _CompositePredicate(*predicates)
        return any(cp(s) for s in self.segments)

    @property
    def raw_slices(self) -> RawFileSlices:
        """Raw slices of the segments."""
        if not self.templated_file:  # pragma: no cover
            raise ValueError(
                'Segments.raw_slices: "templated_file" property is required.'
            )
        raw_slices = set()
        for s in self.segments:
            source_slice = s.pos_marker.source_slice
            raw_slices.update(
                self.templated_file.raw_slices_spanning_source_slice(source_slice)
            )
        return RawFileSlices(self.templated_file, *raw_slices)

    # def with_children(self) -> "Segments":
    #     """Returns an object that includes first-level children."""
    #     raise NotImplementedError

    # def with_descendants(self) -> "Segments":
    #     """Returns an object that includes all descendants."""
    #     raise NotImplementedError

    # def select(
    #     self,
    #     start_seg: Optional[BaseSegment] = None,
    #     stop_seg: Optional[BaseSegment] = None,
    #     select_if=Optional[Sequence[Predicate]],
    #     loop_while=Optional[Sequence[Predicate]],
    # ) -> "Segments":
    #     """Retrieve range/subset."""
    #     raise NotImplementedError

    def delete(self, *predicates: Predicate) -> Sequence["LintFix"]:
        """Return LintFix objects to delete segments that satisfy predicates."""
        cp = _CompositePredicate(*predicates)
        return [LintFix("delete", s) for s in self.segments if cp(s)]


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
