"""Individual segment parsers.

Matchable objects which return individual segments.
"""

from typing import Type, Optional, List, Tuple, Union

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments import RawSegment, BaseSegment


class StringParser(Matchable):
    """An object which matches and returns raw segments based on strings."""

    # Meta segments are handled seperately. All StringParser elements
    # are assumed to be not meta.
    is_meta = False

    def __init__(
        self,
        template: str,
        raw_class: Type[RawSegment],
        name: Optional[str] = None,
        type: Optional[str] = None,
        optional: bool = False,
        **segment_kwargs
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
        self.segment_kwargs = segment_kwargs or {}

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
                    **self.segment_kwargs
                )
                # Return as a tuple
                return MatchResult((new_seg,), segments[1:])
        return MatchResult.from_unmatched(segments)


class NamedParser(StringParser):
    """An object which matches and returns raw segments based on names."""

    def simple(cls, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        NamedParser segment does NOT for now. We might need to later for efficiency.

        There is a way that this *could* be enabled, by allowing *another*
        shortcut route, to look ahead at the names of upcoming segments,
        rather than their content.
        """
        return None

    def match(
        self,
        segments: Union[BaseSegment, Tuple[BaseSegment, ...]],
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Compare input segments for a match, return a `MatchResult`.

        NamedParser implements its own matching function where
        we assume that ._template is the `name` of a segment.
        """
        # If we've been passed the singular, make it a tuple
        if isinstance(segments, BaseSegment):
            segments = (segments,)

        # We're only going to match against the first element
        if len(segments) >= 1:
            seg = segments[0]
            # Case sensitivity is not supported. Names are all
            # lowercase by convention.
            if self.template.lower() == seg.name.lower():
                # Construct the segment object
                new_seg = self.raw_class(
                    raw=seg.raw,
                    pos_marker=seg.pos_marker,
                    type=self.type,
                    name=self.name,
                    **self.segment_kwargs
                )
                # Return as a tuple
                return MatchResult((new_seg,), segments[1:])
        return MatchResult.from_unmatched(segments)
