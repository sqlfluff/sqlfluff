"""The BracketedSegment."""

from typing import TYPE_CHECKING, Optional, Sequence, Set, Tuple

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
        segments: Tuple["BaseSegment", ...],
        # These are tuples of segments but we're expecting them to
        # be tuples of length 1. This is because we'll almost always
        # be doing tuple arithmetic with the results and constructing
        # 1-tuples on the fly is very easy to misread.
        start_bracket: Tuple[BaseSegment],
        end_bracket: Tuple[BaseSegment],
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
    def simple(
        cls, parse_context: ParseContext, crumbs: Optional[Tuple[str, ...]] = None
    ) -> Optional["SimpleHintType"]:
        """Simple methods for bracketed and the persistent brackets."""
        start_brackets = [
            start_bracket
            for _, start_bracket, _, persistent in parse_context.dialect.bracket_sets(
                "bracket_pairs"
            )
            if persistent
        ]
        simple_raws: Set[str] = set()
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
