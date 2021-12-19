"""Surrogate class for working with RawFileSlice collections."""
from typing import Callable, Set, Union

from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFile

Predicate = Union[str, Callable[[RawFileSlice], bool]]


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
        cp = _CompositePredicate(*predicates)
        return all(cp(rs) for rs in self)

    def any(self, *predicates: Predicate) -> bool:
        """Do any of the raw slices match?"""
        cp = _CompositePredicate(*predicates)
        return any(cp(rs) for rs in self)


class _CompositePredicate:
    def __init__(self, *predicates: Predicate):
        self.slice_types: Set[str] = set()
        self.functions = []
        for p in predicates:
            if isinstance(p, str):
                self.slice_types.add(p)
            else:
                self.functions.append(p)

    def __call__(self, raw_slice: RawFileSlice) -> bool:
        if self.slice_types and raw_slice.slice_type not in self.slice_types:
            return False

        if self.functions:
            function_match = False
            p_fn: Callable[[RawFileSlice], bool]
            for p_fn in self.functions:
                if p_fn(raw_slice):
                    function_match = True
                    break
            if not function_match:
                return False

        return True
