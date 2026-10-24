"""Shared descriptions of accepted Python and native parser matches."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, Union

if TYPE_CHECKING:
    from sqlfluff.core.parser.segments import BaseSegment

MetaSegmentExclusions = dict[tuple[str, int, int], tuple[tuple[int, str], ...]]


class MatchResultLike(Protocol):
    """Read-only match metadata shared by the Python and native backends."""

    @property
    def matched_class(self) -> Union[type["BaseSegment"], str, None]:
        """The Python segment class or its native class name."""
        ...

    @property
    def matched_slice(self) -> Union[slice, tuple[int, int]]:
        """The accepted token range in this match's coordinate system."""
        ...

    @property
    def child_matches(self) -> Sequence["MatchResultLike"]:
        """Accepted child matches in source order."""
        ...

    def matches_with_child_class(self, name: str) -> Sequence["MatchResultLike"]:
        """Find parents with a direct child of the named class."""
        ...


def match_class_name(match: MatchResultLike) -> str:
    """Read a segment class name without constructing or converting a tree."""
    cls = match.matched_class
    return cls if isinstance(cls, str) else cls.__name__ if cls else ""


def match_bounds(match: MatchResultLike) -> tuple[int, int]:
    """Read bounded token coordinates from either backend's match metadata."""
    span = match.matched_slice
    if isinstance(span, slice):
        assert span.start is not None and span.stop is not None
        return span.start, span.stop
    return span
