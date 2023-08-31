"""Source for the MatchResult class.

This should be the default response from any `match` method.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Tuple

from sqlfluff.core.parser.helpers import join_segments_raw, trim_non_code_segments

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.segments import BaseSegment


@dataclass(frozen=True)
class MatchResult:
    """This should be the default response from any `match` method.

    Args:
        matched_segments (:obj:`tuple`): A tuple of the segments which have been
            matched in this matching operation.
        unmatched_segments (:obj:`tuple`): A tuple of the segments, which come after
            the `matched_segments` which could not be matched.

    """

    matched_segments: Tuple["BaseSegment", ...] = ()
    unmatched_segments: Tuple["BaseSegment", ...] = ()

    @property
    def trimmed_matched_length(self) -> int:
        """Return the length of the match in characters, trimming whitespace."""
        _, segs, _ = trim_non_code_segments(self.matched_segments)
        return sum(seg.matched_length for seg in segs)

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
        return "<MatchResult {}/{}: {!r}>".format(
            len(self.matched_segments),
            len(self.matched_segments) + len(self.unmatched_segments),
            content,
        )

    @classmethod
    def from_unmatched(cls, unmatched: Tuple["BaseSegment", ...]) -> "MatchResult":
        """Construct a `MatchResult` from just unmatched segments."""
        return cls(matched_segments=(), unmatched_segments=unmatched)

    @classmethod
    def from_matched(cls, matched: Tuple["BaseSegment", ...]) -> "MatchResult":
        """Construct a `MatchResult` from just matched segments."""
        return cls(unmatched_segments=(), matched_segments=matched)

    @classmethod
    def from_empty(cls) -> "MatchResult":
        """Construct an empty `MatchResult`."""
        return cls(unmatched_segments=(), matched_segments=())

    def __add__(self, other: Tuple["BaseSegment", ...]) -> "MatchResult":
        """Override add for concatenating tuples onto this match."""
        return self.__class__(
            matched_segments=self.matched_segments + other,
            unmatched_segments=self.unmatched_segments,
        )
