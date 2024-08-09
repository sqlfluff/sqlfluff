"""Surrogate class for working with RawFileSlice collections."""

from typing import Callable, Optional

from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFile


class RawFileSlices(tuple):
    """Encapsulates a sequence of one or more RawFileSlice.

    The slices may or may not be contiguous in a file.
    Provides useful operations on a sequence of slices to simplify rule creation.
    """

    def __new__(cls, *raw_slices, templated_file=None):
        """Override new operator."""
        return super(RawFileSlices, cls).__new__(cls, raw_slices)

    def __init__(self, *_: RawFileSlice, templated_file: TemplatedFile):
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

    def select(
        self,
        select_if: Optional[Callable[[RawFileSlice], bool]] = None,
        loop_while: Optional[Callable[[RawFileSlice], bool]] = None,
        start_slice: Optional[RawFileSlice] = None,
        stop_slice: Optional[RawFileSlice] = None,
    ) -> "RawFileSlices":
        """Retrieve range/subset.

        NOTE: Iterates the slices BETWEEN start_slice and stop_slice, i.e. those
        slices are not included in the loop.
        """
        start_index = self.index(start_slice) if start_slice else -1
        stop_index = self.index(stop_slice) if stop_slice else len(self)
        buff = []
        for slice_ in self[start_index + 1 : stop_index]:
            if loop_while is not None and not loop_while(slice_):
                # NOTE: This likely needs more tests.
                break  # pragma: no cover
            if select_if is None or select_if(slice_):
                buff.append(slice_)
        return RawFileSlices(*buff, templated_file=self.templated_file)
