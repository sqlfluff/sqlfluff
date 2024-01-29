"""Complex Type helpers."""

from enum import Enum
from typing import TYPE_CHECKING, FrozenSet, Optional, Tuple, Union

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.matchable import Matchable
    from sqlfluff.core.parser.segments.generator import SegmentGenerator

# When defining elements of a dialect they can be matchables or generators.
DialectElementType = Union["Matchable", "SegmentGenerator"]

# Simple hints has a set of strings first and a set of types second.
SimpleHintType = Optional[Tuple[FrozenSet[str], FrozenSet[str]]]

# The content type of the set of bracket pairs.
# bracket_type, start_ref, end_ref, persists
BracketPairTuple = Tuple[str, str, str, bool]

# Define the potential parse modes. These are used in grammars
# to define how greedy they are in claiming unmatched segments.
# While the default is to only claim what they can match this
# can make pinpointing unparsable sections very difficult. By
# occasionally allowing more eager matching (for example in the
# content of bracketed expressions), we can provide more helpful
# feedback to the user.
ParseMode = Enum(
    "ParseMode",
    [
        # Strict only returns a match if the full content matches.
        # i.e. if it's not a successful match, then don't return _any_
        # match and never raise unparsable sections.
        # NOTE: This is the default for all grammars.
        "STRICT",
        # Greedy will always return a match, providing there is at least
        # one code element before a terminators. Terminators are not included
        # in the match, but are searched for before matching any content. Segments
        # which are part of any terminator (or beyond) are not available for
        # matching by any content.
        # NOTE: This replicates the `GreedyUntil` semantics.
        "GREEDY",
        # Optionally, a variant on "GREEDY", will return behave like "STRICT"
        # if nothing matches, but behaves like "GREEDY" once something has
        # matched.
        # NOTE: This replicates the `StartsWith` semantics.
        "GREEDY_ONCE_STARTED",
        # TODO: All of the existing modes here match terminators _before_
        # matching the majority of content. While that is safer, there should
        # be room for more efficient parsing modes in some cases.
    ],
)
