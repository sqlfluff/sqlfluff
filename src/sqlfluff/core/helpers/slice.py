"""Helpers for handling slices."""

from typing import Tuple


def to_tuple(s: slice) -> Tuple[int, int]:
    """Convert a slice into a tuple of (start, stop)."""
    assert s.start is not None and s.stop is not None
    return (s.start, s.stop)


def slice_length(s: slice) -> int:
    """Get the length of a slice."""
    length: int = s.stop - s.start
    return length


def is_zero_slice(s: slice) -> bool:
    """Return true if this is a zero slice."""
    is_zero: bool = s.stop == s.start
    return is_zero


def zero_slice(i: int) -> slice:
    """Construct a zero slice from a single integer."""
    return slice(i, i)


def offset_slice(start: int, offset: int) -> slice:
    """Construct a slice from a start and offset."""
    return slice(start, start + offset)


def slice_overlaps(s1: slice, s2: slice) -> bool:
    """Check whether two slices overlap.

    NOTE: This is designed only for use with *closed* and
    *positive* slices.
    """
    assert s1.start is not None, f"{s1} is not closed"
    assert s1.stop is not None, f"{s1} is not closed"
    assert s2.start is not None, f"{s2} is not closed"
    assert s2.stop is not None, f"{s2} is not closed"
    assert s1.start <= s1.stop, f"{s1} is not positive"
    assert s2.start <= s2.stop, f"{s2} is not positive"

    if s2.start >= s1.stop:
        return False

    if s1.start >= s2.stop:
        return False

    return True
