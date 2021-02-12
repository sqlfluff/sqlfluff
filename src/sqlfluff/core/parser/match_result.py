"""Source for the MatchResult class.

This should be the default response from any `match` method.
"""

from typing import Tuple, TYPE_CHECKING
from collections import namedtuple

from sqlfluff.core.parser.helpers import join_segments_raw

if TYPE_CHECKING:
    from sqlfluff.core.parser.segments import BaseSegment


def is_segment(other):
    """Return true if this is a Segment.

    The purpose of this helper function is for testing if something
    is a segment without requiring the import of the class.
    """
    return getattr(other, "is_segment", False)


class MatchResult(
    namedtuple("MatchResult", ["matched_segments", "unmatched_segments"])
):
    """This should be the default response from any `match` method.

    Args:
        matched_segments (:obj:`tuple`): A tuple of the segments which have been
            matched in this matching operation.
        unmatched_segments (:obj:`tuple`): A tuple of the segments, which come after
            the `matched_segments` which could not be matched.

    """

    @property
    def matched_length(self) -> int:
        """Return the length of the match in characters."""
        return sum(seg.matched_length for seg in self.matched_segments)

    def all_segments(self) -> Tuple["BaseSegment", ...]:
        """Return a tuple of all the segments, matched or otherwise."""
        return self.matched_segments + self.unmatched_segments

    def __len__(self) -> int:
        return len(self.matched_segments)

    def is_complete(self) -> bool:
        """Return true if everything has matched.

        Note: An empty match is not a match so will return False.
        """
        return len(self.unmatched_segments) == 0 and len(self.matched_segments) > 0

    def has_match(self) -> bool:
        """Return true if *anything* has matched."""
        return len(self) > 0

    def __bool__(self) -> bool:
        return self.has_match()

    def raw_matched(self) -> str:
        """Make a string from the raw matched segments."""
        return join_segments_raw(self.matched_segments)

    def __str__(self) -> str:
        content = self.raw_matched()
        # Clip the content if it's long.
        # The ends are the important bits.
        if len(content) > 32:
            content = content[:15] + "..." + content[-15:]
        return "<MatchResult {0}/{1}: {2!r}>".format(
            len(self.matched_segments),
            len(self.matched_segments) + len(self.unmatched_segments),
            content,
        )

    def __eq__(self, other):
        """Equals function override.

        This allows comparison to tuples for testing.
        """
        if isinstance(other, MatchResult):
            return (
                self.matched_segments == other.matched_segments
                and self.unmatched_segments == other.unmatched_segments
            )
        elif isinstance(other, tuple):
            return self.matched_segments == other
        else:
            raise TypeError(
                "Unexpected equality comparison: type: {0}".format(type(other))
            )

    @staticmethod
    def seg_to_tuple(segs):
        """Munge types to a tuple."""
        # Is other iterable?
        try:
            iterator = iter(segs)
        except TypeError:
            is_iterable = False
        else:
            is_iterable = True

        if is_segment(segs):
            return (segs,)
        elif is_iterable:
            return tuple(iterator)
        else:
            raise TypeError("Unexpected input to `seg_to_tuple`: {0}".format(segs))

    @classmethod
    def from_unmatched(cls, unmatched) -> "MatchResult":
        """Construct a `MatchResult` from just unmatched segments."""
        return cls(matched_segments=(), unmatched_segments=cls.seg_to_tuple(unmatched))

    @classmethod
    def from_matched(cls, matched) -> "MatchResult":
        """Construct a `MatchResult` from just matched segments."""
        return cls(unmatched_segments=(), matched_segments=cls.seg_to_tuple(matched))

    @classmethod
    def from_empty(cls) -> "MatchResult":
        """Construct an empty `MatchResult`."""
        return cls(unmatched_segments=(), matched_segments=())

    def __add__(self, other) -> "MatchResult":
        """Override add for concatenating things onto this match."""
        if isinstance(other, MatchResult):
            return self.__class__(
                matched_segments=self.matched_segments + other.matched_segments,
                unmatched_segments=self.unmatched_segments,
            )
        else:
            try:
                other_tuple = self.seg_to_tuple(other)
            except TypeError:
                raise TypeError(
                    "Unexpected type passed to MatchResult.__add__: {0}".format(
                        type(other)
                    )
                )
            if len(other_tuple) > 0 and not is_segment(other_tuple[0]):
                raise TypeError(
                    "Unexpected type passed to MatchResult.__add__: {2} of {0}.\n{1}".format(
                        type(other[0]), other_tuple, type(other)
                    )
                )
            return self.__class__(
                matched_segments=self.matched_segments + other_tuple,
                unmatched_segments=self.unmatched_segments,
            )
