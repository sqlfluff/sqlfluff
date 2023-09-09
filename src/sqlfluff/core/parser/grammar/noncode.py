"""A non-code matcher.

This is a stub of a grammar, intended for use entirely as a
terminator or similar alongside other matchers.
"""

from typing import Optional, Tuple

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
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

    @match_wrapper(v_level=4)
    def match(
        self, segments: Tuple[BaseSegment, ...], parse_context: ParseContext
    ) -> MatchResult:
        """Match any starting non-code segments."""
        if not isinstance(segments, tuple):  # pragma: no cover
            raise TypeError("NonCodeMatcher expects a tuple.")
        idx = 0
        while idx < len(segments) and not segments[idx].is_code:
            idx += 1
        return MatchResult(segments[:idx], segments[idx:])
