"""Surrogate class for working with RawFileSlice collections."""
from typing import Callable, Optional

from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFile


class RawFileSlices(tuple):
    """Encapsulates a sequence of one or more RawFileSlice.

    The slices may or may not be contiguous in a file.
    Provides useful operations on a sequence of slices to simplify rule creation.
    """

    def __new__(cls, templated_file, *raw_slices):
        """Override new operator."""
        return super(RawFileSlices, cls).__new__(cls, raw_slices)

    def __init__(self, templated_file: TemplatedFile, *_: RawFileSlice):
        self.templated_file = templated_file

    def all(self, predicate: Optional[Callable[[RawFileSlice], bool]] = None) -> bool:
        """Do all the raw slices match?"""
        for s in self:
            if predicate is not None and not predicate(s):
                return False
        return True

    def any(self, predicate: Optional[Callable[[RawFileSlice], bool]] = None) -> bool:
        """Do any of the raw slices match?"""
        for s in self:
            if predicate is None or predicate(s):
                return True
        return False
