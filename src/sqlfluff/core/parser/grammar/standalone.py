"""A matcher for elements which must stand alone on a line of their own.

Some dialects use a delimiter which is only meaningful when it occupies a
line by itself. A good example is the SQL*Plus ``/`` batch delimiter in
Oracle, which terminates and runs the preceding statement rather than
being an operator. Treating such a delimiter as a normal terminator is too
eager (it would also match ``1 / 100``), while not treating it as a
terminator at all means the statement parser swallows it.

This matcher wraps another matcher and only allows it to match when the
line before and after it contains no other code.
"""

from collections.abc import Sequence
from typing import Optional

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.parser.types import SimpleHintType


class StandaloneLineMatcher(Matchable):
    """Match an inner matcher only when it stands alone on its own line.

    Args:
        matcher: The matcher to use for the element itself. Its ``simple()``
            hint is also used to drive the fast lookup path in
            :func:`sqlfluff.core.parser.match_algorithms.next_match`.
    """

    def __init__(self, matcher: Matchable) -> None:
        self.matcher = matcher

    def is_optional(self) -> bool:
        """A standalone line matcher is never optional."""
        return False

    def simple(
        self, parse_context: ParseContext, crumbs: Optional[tuple[str, ...]] = None
    ) -> SimpleHintType:
        """Delegate to the inner matcher."""
        return self.matcher.simple(parse_context=parse_context, crumbs=crumbs)

    def cache_key(self) -> str:
        """Get the cache key for the matcher."""
        return "standalone-line-" + self.matcher.cache_key()

    @staticmethod
    def _skip_gaps_forward(segments: Sequence[BaseSegment], idx: int) -> int:
        """Move ``idx`` forward past any whitespace or meta segments."""
        while idx < len(segments) and (
            segments[idx].is_meta or segments[idx].is_type("whitespace")
        ):
            idx += 1
        return idx

    @staticmethod
    def _skip_gaps_backward(segments: Sequence[BaseSegment], idx: int) -> int:
        """Move ``idx`` backward past any whitespace or meta segments."""
        while idx >= 0 and (
            segments[idx].is_meta or segments[idx].is_type("whitespace")
        ):
            idx -= 1
        return idx

    def match(
        self,
        segments: Sequence[BaseSegment],
        idx: int,
        parse_context: ParseContext,
    ) -> MatchResult:
        """Match when the inner matcher matches and it is alone on its line.

        "Alone" means that from the start of the line up to the match, and
        from the end of the match to the end of the line, there is nothing
        except whitespace, meta segments or the newline itself. A match at the
        very beginning or end of the file is also considered standalone. A
        comment on the same line prevents the match: SQL*Plus requires its
        slash command to occupy a line by itself.
        """
        inner_match = self.matcher.match(segments, idx, parse_context)
        if not inner_match:
            return MatchResult.empty_at(idx)

        # Check the content of the line before the match.
        before = self._skip_gaps_backward(segments, idx - 1)
        if before >= 0 and not segments[before].is_type("newline"):
            return MatchResult.empty_at(idx)

        # Check the content of the line after the match.
        after = self._skip_gaps_forward(segments, inner_match.matched_slice.stop)
        if after < len(segments) and not segments[after].is_type("newline"):
            return MatchResult.empty_at(idx)

        return inner_match
