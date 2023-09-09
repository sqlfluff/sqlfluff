"""Complex Type helpers."""
from typing import TYPE_CHECKING, FrozenSet, Optional, Tuple, Type, Union

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.matchable import Matchable
    from sqlfluff.core.parser.segments.base import BaseSegment
    from sqlfluff.core.parser.segments.generator import SegmentGenerator

# When defining elements of a dialect they can be matchables, segments or generators.
DialectElementType = Union[Type["BaseSegment"], "Matchable", "SegmentGenerator"]

# Either a Matchable (a grammar or parser) or a Segment CLASS
# NOTE: Post expansion, no generators remain
MatchableType = Union["Matchable", Type["BaseSegment"]]

# Simple hints has a set of strings first and a set of types second.
SimpleHintType = Optional[Tuple[FrozenSet[str], FrozenSet[str]]]

# The content type of the set of bracket pairs.
# bracket_type, start_ref, end_ref, persists
BracketPairTuple = Tuple[str, str, str, bool]
