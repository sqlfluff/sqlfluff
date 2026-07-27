"""A newline matcher.

Stub grammar for use as a terminator: matches newline segments only,
not generic whitespace. Useful for statement-boundary termination where
intra-line spaces must remain part of the matched content.
"""

from collections.abc import Sequence
from typing import Optional

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.parser.types import SimpleHintType


class NewlineMatcher(Matchable):
    """Match a single newline segment.

    Like ``NonCodeMatcher``, this is intended as a terminator. Unlike
    ``NonCodeMatcher``, whitespace and comments are not treated as a match,
    so opaque values may still contain spaces.
    """

    def simple(
        self, parse_context: ParseContext, crumbs: Optional[tuple[str, ...]] = None
    ) -> SimpleHintType:
        """This element doesn't work with simple."""
        return None

    def is_optional(self) -> bool:  # pragma: no cover
        """Not optional."""
        return False

    def cache_key(self) -> str:
        """Get the cache key for the matcher."""
        return "newline-matcher"

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match a newline at the current position."""
        if idx < len(segments) and segments[idx].is_type("newline"):
            return MatchResult(matched_slice=slice(idx, idx + 1))
        return MatchResult.empty_at(idx)
