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
        preceding_sequences: Ordered tuples of uppercase keyword strings
            that may appear immediately before the current position, where
            matching is performed from right to left within each sequence
            (i.e. the last item is checked first). Non-code and meta
            segments between keywords are skipped.
    """

    def __init__(
        self,
        preceding_sequences: tuple[tuple[str, ...], ...],
    ) -> None:
        self.preceding_sequences = preceding_sequences

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
        return "preceded-by-" + "|".join(
            "-".join(sequence) for sequence in self.preceding_sequences
        )

    @staticmethod
    def _skip_non_code_and_meta_backward(
        segments: Sequence["BaseSegment"],
        idx: int,
    ) -> int:
        """Move ``idx`` backward past any non-code or meta segments."""
        while idx >= 0 and (not segments[idx].is_code or segments[idx].is_meta):
            idx -= 1
        return idx

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match when the position is preceded by the configured keywords.

        Scans backward from ``idx`` through non-code and meta segments,
        checking each candidate keyword sequence defined in
        ``preceding_sequences``. Each sequence is checked right-to-left,
        i.e. the last element of a sequence must appear closest to the
        current position.

        Returns a non-empty :class:`MatchResult` if the lookbehind matches
        (meaning the caller's ``exclude`` should suppress the outer match),
        or an empty result if it does not match.
        """
        for preceding in self.preceding_sequences:
            if self._match_preceding_sequence(segments, idx, preceding):
                return MatchResult(slice(idx, idx + 1))

        return MatchResult.empty_at(idx)

    def _match_preceding_sequence(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        preceding: tuple[str, ...],
    ) -> bool:
        """Return whether a specific preceding sequence matches."""
        prev = idx - 1

        for keyword in reversed(preceding):
            prev = self._skip_non_code_and_meta_backward(segments, prev)
            if prev < 0 or segments[prev].raw_upper != keyword:
                return False
            prev -= 1

        return True


# Shared exclude pattern for the FROM keyword in select clause terminators.
# Prevents FROM in "IS [NOT] DISTINCT FROM" being treated as a FROM clause.
is_distinct_from_lookbehind = PrecededByMatcher(
    preceding_sequences=(("IS", "DISTINCT"), ("IS", "NOT", "DISTINCT")),
)
