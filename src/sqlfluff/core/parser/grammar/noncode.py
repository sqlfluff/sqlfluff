"""A non-code matcher.

This is a stub of a grammar, intended for use entirely as a
terminator or similar alongside other matchers.
"""

from typing import Optional, Sequence, Tuple

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.parser.types import SimpleHintType


class NonCodeMatcher(Matchable):
    """An object which behaves like a matcher to match non-code."""

    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str, ...]] = None
    ) -> SimpleHintType:
        """This element doesn't work with simple."""
        return None

    def is_optional(self) -> bool:  # pragma: no cover
        """Not optional.

        NOTE: The NonCodeMatcher is only normally only used as a terminator
        or other special instance matcher. As such the `.simple()` method
        is unlikely to be used.
        """
        return False

    def cache_key(self) -> str:
        """Get the cache key for the matcher.

        NOTE: In this case, this class is a bit of a singleton
        and so we don't need a unique UUID in the same way as
        other classes.
        """
        return "non-code-matcher"

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match any starting non-code segments."""
        matched_idx = idx
        for matched_idx in range(idx, len(segments)):
            if segments[matched_idx].is_code:
                break
        if matched_idx > idx:
            return MatchResult(matched_slice=slice(idx, matched_idx))
        # Otherwise return no match
        return MatchResult.empty_at(idx)
