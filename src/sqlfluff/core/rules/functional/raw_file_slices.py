"""Surrogate class for working with RawFileSlice collections."""
from typing import Callable

from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFile

Predicate = Callable[[RawFileSlice], bool]


class RawFileSlices(list):
    """Encapsulates a sequence of one or more RawFileSlice.

    The slices may or may not be contiguous in a file.
    Provides useful operations on a sequence of slices to simplify rule creation.
    """

    def __new__(cls, templated_file, *raw_slices):
        """Override new operator."""
        return super(RawFileSlices, cls).__new__(cls, raw_slices)

    def __init__(self, templated_file: TemplatedFile, *raw_slices: RawFileSlice):
        super().__init__(raw_slices)
        self.templated_file = templated_file

    def all(self, *predicates: Predicate) -> bool:
        """Do all the raw slices match?"""
        for s in self:
            if predicates and not any(p(s) for p in predicates):
                return False
        return True

    def any(self, *predicates: Predicate) -> bool:
        """Do any of the raw slices match?"""
        for s in self:
            if not predicates or any(p(s) for p in predicates):
                return True
        return False
