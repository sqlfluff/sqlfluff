"""Defines commonly used templated file slice predicates for rule writers.

For consistency, all the predicates in this module are implemented as functions
returning functions. This avoids rule writers having to remember the
distinction between normal functions and functions returning functions.

This is not necessarily a complete set of predicates covering all possible
requirements. Rule authors can define their own predicates as needed, either
as regular functions, `lambda`, etc.
"""

from typing import Callable

from sqlfluff.core.templaters.base import TemplatedFileSlice


def is_slice_type(
    *slice_types: str,
) -> Callable[[TemplatedFileSlice], bool]:
    """Returns a function that determines if segment is one the types."""

    def _(raw_slice: TemplatedFileSlice) -> bool:
        return any(raw_slice.slice_type == slice_type for slice_type in slice_types)

    return _
