"""Individual segment parsers.

Matchable objects which return individual segments.
"""

from typing import Type, Optional, List, Tuple, Union

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments import RawSegment, BaseSegment


class StringParser(Matchable):
    """An object which matches and returns raw segments base on strings."""

    def __init__(
        self,
        template: str,
        raw_class: Type[RawSegment],
        name: Optional[str] = None,
        type: Optional[str] = None,
        optional: bool = False,
    ):
        # String matchers are not case sensitive, so we make the template
        # uppercase on creation. If any SQL dialect is found to be case
        # sensitive for keywords, this could be extended to allow
        # case sentivitiy.
        self.template = template.upper()
        self.raw_class = raw_class
        self.name = name
        self.type = type
        self.optional = optional

    def is_optional(self) -> bool:
        """Return whether this element is optional."""
        return self.optional

    def simple(self, parse_context: "ParseContext") -> Optional[List[str]]:
        """Return simple options for this matcher.

        Because string matchers are not case sensitive we can
        just return the template here.
        """
        return [self.template]

    def match(
        self,
        segments: Union[BaseSegment, Tuple[BaseSegment, ...]],
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Compare input segments for a match, return a `MatchResult`.

        Note: For matching here, we only consider the *first* element,
        because we assume that a keyword can only span one raw segment.
        """
        # If we've been passed the singular, make it a tuple
        if isinstance(segments, BaseSegment):
            segments = (segments,)

        # We're only going to match against the first element
        if len(segments) >= 1:
            seg = segments[0]
            raw_comp = seg.raw.upper()

            # Is the target a match and IS IT CODE.
            # The latter stops us accidentally matching comments.
            if self.template == raw_comp and seg.is_code:
                # Construct the segment object
                new_seg = self.raw_class(
                    raw=seg.raw,
                    pos_marker=seg.pos_marker,
                    type=self.type,
                    name=self.name,
                )
                # Return as a tuple
                return MatchResult((new_seg,), segments[1:])
        return MatchResult.from_unmatched(segments)
