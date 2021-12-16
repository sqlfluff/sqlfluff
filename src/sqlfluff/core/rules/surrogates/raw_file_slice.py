"""Surrogate class for working with RawFileSlice collections."""
from typing import Callable, Set, TypeVar

from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFile

Predicate = TypeVar("Predicate", str, Callable[[RawFileSlice], bool])


class RawFileSlices:
    """Encapsulates a sequence of one or more RawFileSlice.

    The slices may or may not be contiguous in a file.
    Provides useful operations on a sequence of slices to simplify rule creation.
    """

    def __init__(self, templated_file: TemplatedFile, *raw_slices: RawFileSlice):
        self.templated_file = templated_file
        self.raw_slices = raw_slices

    def all(self, *predicates: Predicate) -> bool:
        """Do all the raw slices match?"""
        cp = _CompositePredicate(*predicates)
        return all(cp(rs) for rs in self.raw_slices)

    def any(self, *predicates: Predicate) -> bool:
        """Do any of the raw slices match?"""
        cp = _CompositePredicate(*predicates)
        return any(cp(rs) for rs in self.raw_slices)


class _CompositePredicate:
    def __init__(self, *predicates: Predicate):
        self.slice_types: Set[str] = set()
        self.other = []
        for p in predicates:
            if isinstance(p, str):
                self.slice_types.add(p)
            else:
                self.other.append(p)

    def __call__(self, raw_slice: RawFileSlice) -> bool:
        if self.slice_types and raw_slice.slice_type not in self.slice_types:
            return False

        for p in self.other:
            if not p(raw_slice):  # Arbitrary function
                return False
        return True
