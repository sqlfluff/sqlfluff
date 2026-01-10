"""The BracketedSegment."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Optional

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments.base import BaseSegment

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.types import SimpleHintType


class BracketedSegment(BaseSegment):
    """A segment containing a bracketed expression."""

    type = "bracketed"
    additional_kwargs = ["start_bracket", "end_bracket"]

    def __init__(
        self,
        segments: tuple["BaseSegment", ...],
        # These are tuples of segments but we're expecting them to
        # be tuples of length 1. This is because we'll almost always
        # be doing tuple arithmetic with the results and constructing
        # 1-tuples on the fly is very easy to misread.
        start_bracket: tuple[BaseSegment],
        end_bracket: tuple[BaseSegment],
        pos_marker: Optional[PositionMarker] = None,
        uuid: Optional[int] = None,
    ):
        """Stash the bracket segments for later."""
        if not start_bracket or not end_bracket:  # pragma: no cover
            raise ValueError(
                "Attempted to construct Bracketed segment without specifying brackets."
            )
        self.start_bracket = start_bracket
        self.end_bracket = end_bracket
        super().__init__(segments=segments, pos_marker=pos_marker, uuid=uuid)

    @classmethod
    def from_result_segments(
        cls,
        result_segments: tuple[BaseSegment, ...],
        segment_kwargs: dict[str, Any],
    ) -> BaseSegment:
        """Create BracketedSegment from result segments.

        When called from Rust parser, start_bracket and end_bracket won't be in
        segment_kwargs, so we extract them from the first and last result segments.
        """
        # If start_bracket and end_bracket are already provided, use them
        if "start_bracket" in segment_kwargs and "end_bracket" in segment_kwargs:
            return cls(segments=result_segments, **segment_kwargs)

        # Otherwise extract from result_segments (Rust parser path)
        if len(result_segments) < 2:  # pragma: no cover
            raise ValueError(
                f"BracketedSegment requires at least 2 child segments "
                f"(open and close brackets), got {len(result_segments)}"
            )

        # First segment is start_bracket, last is end_bracket
        return cls(
            segments=result_segments,
            start_bracket=(result_segments[0],),
            end_bracket=(result_segments[-1],),
            **segment_kwargs,
        )

    @classmethod
    def simple(
        cls, parse_context: ParseContext, crumbs: Optional[tuple[str, ...]] = None
    ) -> Optional["SimpleHintType"]:
        """Simple methods for bracketed and the persistent brackets."""
        start_brackets = [
            start_bracket
            for _, start_bracket, _, persistent in parse_context.dialect.bracket_sets(
                "bracket_pairs"
            )
            if persistent
        ]
        simple_raws: set[str] = set()
        for ref in start_brackets:
            bracket_simple = parse_context.dialect.ref(ref).simple(
                parse_context, crumbs=crumbs
            )
            assert bracket_simple, "All bracket segments must support simple."
            assert bracket_simple[0], "All bracket segments must support raw simple."
            # NOTE: By making this assumption we don't have to handle the "typed"
            # simple here.
            simple_raws.update(bracket_simple[0])
        return frozenset(simple_raws), frozenset()

    @classmethod
    def match(
        cls,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Only useful as a terminator.

        NOTE: Coverage of this method is poor, because in typical use
        as a terminator - the `.simple()` method covers everything we
        need.
        """
        if isinstance(segments[idx], cls):  # pragma: no cover
            return MatchResult(slice(idx, idx + 1))
        return MatchResult.empty_at(idx)
