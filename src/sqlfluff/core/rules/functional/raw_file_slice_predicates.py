"""Defines commonly used raw file slice predicates for rule writers.

This is not necessarily a complete set of predicates covering all possible
requirements. Rule authors can define their own predicates as needed.
"""
from typing import Callable

from sqlfluff.core.templaters.base import RawFileSlice


def is_slice_type(
    *slice_types: str,
) -> Callable[[RawFileSlice], bool]:
    """Returns a function that determines if segment is one the types."""

    def _(raw_slice: RawFileSlice):
        return any(raw_slice.slice_type == slice_type for slice_type in slice_types)

    return _
