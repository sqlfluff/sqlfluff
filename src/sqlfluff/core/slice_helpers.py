"""Helpers for handling slices."""

from typing import Tuple


def to_tuple(s: slice) -> Tuple[int, int]:
    """Convert a slice into a tuple of (start, stop)."""
    assert s.start is not None and s.stop is not None
    return (s.start, s.stop)


def slice_length(s: slice) -> int:
    """Get the length of a slice."""
    return s.stop - s.start


def is_zero_slice(s: slice) -> bool:
    """Return true if this is a zero slice."""
    return s.stop == s.start


def zero_slice(i: int) -> slice:
    """Construct a zero slice from a single integer."""
    return slice(i, i)


def offset_slice(start: int, offset: int) -> slice:
    """Construct a slice from a start and offset."""
    return slice(start, start + offset)
