"""A lookbehind matcher for keyword disambiguation.

This is a stub of a grammar, intended for use as an ``exclude`` pattern
on keyword terminators to prevent them from matching when preceded by
specific keyword sequences.
"""

from collections.abc import Sequence
from typing import Optional

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.parser.types import SimpleHintType


class PrecededByMatcher(Matchable):
    """Matches when the current position is preceded by a keyword sequence.

    This is used as an ``exclude`` pattern on keyword matchers to prevent
    them from matching when preceded by specific keyword sequences.

    For example, it prevents ``FROM`` in ``IS [NOT] DISTINCT FROM`` from
    being treated as the start of a ``FROM`` clause when used as an exclude
    on the ``FROM`` keyword in ``SelectClauseTerminatorGrammar``.

    Args:
        preceding: An ordered tuple of uppercase keyword strings that
            must appear (in order, right-to-left) immediately before the
            current position. Whitespace and meta segments between
            keywords are skipped.
        optional_preceding: An optional set of uppercase keyword strings.
            Between each pair of required keywords, if the keyword at the
            current lookbehind position matches any of these, it is consumed
            (skipping whitespace/meta) before continuing to check the next
            required keyword. This handles optional keywords like ``NOT``
            in ``IS [NOT] DISTINCT FROM``.
    """

    def __init__(
        self,
        preceding: tuple[str, ...],
        optional_preceding: tuple[str, ...] = (),
    ) -> None:
        self.preceding = preceding
        self.optional_preceding = optional_preceding

    def is_optional(self) -> bool:  # pragma: no cover
        """Return whether this element is optional.

        A lookbehind matcher is never optional — it must always be evaluated.
        """
        return False

    def simple(
        self, parse_context: ParseContext, crumbs: Optional[tuple[str, ...]] = None
    ) -> SimpleHintType:  # pragma: no cover
        """This element doesn't work with simple."""
        return None

    def cache_key(self) -> str:  # pragma: no cover
        """Get the cache key for the matcher."""
        return (
            f"preceded-by-{'-'.join(self.preceding)}"
            f"-opt-{'-'.join(self.optional_preceding)}"
        )

    @staticmethod
    def _skip_whitespace_and_meta_backward(
        segments: Sequence["BaseSegment"],
        idx: int,
    ) -> int:
        """Move ``idx`` backward past any whitespace or meta segments."""
        while idx >= 0 and (segments[idx].is_whitespace or segments[idx].is_meta):
            idx -= 1
        return idx

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match when the position is preceded by the configured keywords.

        Scans backward from ``idx`` through whitespace and meta segments,
        checking for the keyword sequence defined in ``preceding`` (checked
        right-to-left, i.e. the last element of ``preceding`` must appear
        closest to the current position).

        Between each pair of required keywords, any single keyword from
        ``optional_preceding`` is consumed if present.

        Returns a non-empty :class:`MatchResult` if the lookbehind matches
        (meaning the caller's ``exclude`` should suppress the outer match),
        or an empty result if it does not match.
        """
        prev = idx - 1

        for i, keyword in enumerate(reversed(self.preceding)):
            prev = self._skip_whitespace_and_meta_backward(segments, prev)
            if prev < 0 or segments[prev].raw_upper != keyword:
                return MatchResult.empty_at(idx)
            prev -= 1

            # Between required keywords, try to consume one optional keyword.
            if i < len(self.preceding) - 1 and self.optional_preceding:
                _prev = self._skip_whitespace_and_meta_backward(segments, prev)
                if _prev >= 0 and segments[_prev].raw_upper in self.optional_preceding:
                    prev = _prev - 1

        # All preceding keywords matched — the lookbehind is satisfied.
        return MatchResult(slice(idx, idx + 1))
