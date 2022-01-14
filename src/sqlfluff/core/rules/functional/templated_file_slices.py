"""Surrogate class for working with TemplatedFileSlice collections."""
from typing import Callable, Optional

from sqlfluff.core.templaters.base import TemplatedFileSlice, TemplatedFile


class TemplatedFileSlices(tuple):
    """Encapsulates a sequence of one or more TemplatedFileSlice.

    The slices may or may not be contiguous in a file.
    Provides useful operations on a sequence of slices to simplify rule creation.
    """

    def __new__(cls, *raw_slices, templated_file=None):
        """Override new operator."""
        return super(TemplatedFileSlices, cls).__new__(cls, raw_slices)

    def __init__(self, *_: TemplatedFileSlice, templated_file: TemplatedFile):
        self.templated_file = templated_file

    def all(
        self, predicate: Optional[Callable[[TemplatedFileSlice], bool]] = None
    ) -> bool:
        """Do all the templated slices match?"""
        for s in self:
            if predicate is not None and not predicate(s):
                return False
        return True

    def any(
        self, predicate: Optional[Callable[[TemplatedFileSlice], bool]] = None
    ) -> bool:  # pragma: no cover
        """Do any of the templated slices match?"""
        for s in self:
            if predicate is None or predicate(s):
                return True
        return False
