"""Individual segment parsers.

Matchable objects which return individual segments.
"""

from abc import abstractmethod
from uuid import uuid4
import regex
from typing import Collection, Type, Optional, Tuple, Union

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.segments import RawSegment, BaseSegment


class BaseParser(Matchable):
    """An abstract class from which other Parsers should inherit."""

    # Meta segments are handled separately. All Parser elements
    # are assumed to be not meta.
    is_meta: bool = False

    @abstractmethod
    def __init__(
        self,
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        **segment_kwargs,
    ) -> None:
        self.raw_class = raw_class
        self.type = type
        self.optional = optional
        self.segment_kwargs = segment_kwargs or {}
        # Generate a cache key
        self._cache_key = uuid4().hex

    def cache_key(self) -> str:
        """Get the cache key for this parser.

        For parsers, they're unique per-instance.
        """
        return self._cache_key

    def is_optional(self) -> bool:
        """Return whether this element is optional."""
        return self.optional

    @abstractmethod
    def _is_first_match(self, segment: BaseSegment):
        """Does the segment provided match according to the current rules."""

    def _make_match_from_segment(self, segment: BaseSegment):
        """Make a MatchResult from the first segment in the given list.

        This is a helper function for reuse by other parsers.
        """
        # Construct the segment object
        new_seg = self.raw_class(
            raw=segment.raw,
            pos_marker=segment.pos_marker,
            type=self.type,
            **self.segment_kwargs,
        )
        # Return as a tuple
        return new_seg

    def _match_single(self, segment: BaseSegment):
        """Match a single segment.

        Used in the context of matching against the first in a sequence.
        """
        # Is the segment already of this type?
        if isinstance(segment, self.raw_class) and segment.is_type(self.type):
            return segment
        # Does it match?
        elif self._is_first_match(segment):
            return self._make_match_from_segment(segment)

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
            seg = self._match_single(segments[0])
            if seg:
                return MatchResult((seg,), segments[1:])

        return MatchResult.from_unmatched(segments)


class TypedParser(BaseParser):
    """An object which matches and returns raw segments based on types."""

    def __init__(
        self,
        template: str,
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        **segment_kwargs,
    ):
        # NB: the template in this case is the _target_ type.
        # The type kwarg is the eventual type.
        self.template = template
        super().__init__(
            raw_class=raw_class,
            # If no type specified we default to the template
            type=type or template,
            optional=optional,
            **segment_kwargs,
        )

    def simple(cls, parse_context: ParseContext, crumbs=None):
        """Does this matcher support a uppercase hash matching route?

        TypedParser segment doesn't support matching against raw strings,
        but it does support it against types.
        """
        return frozenset(), frozenset((cls.template,))

    def _is_first_match(self, segment: BaseSegment):
        """Return true if the type matches the target type."""
        return segment.is_type(self.template)


class StringParser(BaseParser):
    """An object which matches and returns raw segments based on strings."""

    def __init__(
        self,
        template: str,
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        **segment_kwargs,
    ):
        self.template = template.upper()
        # Create list version upfront to avoid recreating it multiple times.
        self._simple = frozenset((self.template,))
        super().__init__(
            raw_class=raw_class,
            type=type,
            optional=optional,
            **segment_kwargs,
        )

    def simple(self, parse_context: "ParseContext", crumbs=None):
        """Return simple options for this matcher.

        Because string matchers are not case sensitive we can
        just return the template here.
        """
        return self._simple, frozenset()

    def _is_first_match(self, segment: BaseSegment):
        """Does the segment provided match according to the current rules."""
        # Is the target a match and IS IT CODE.
        # The latter stops us accidentally matching comments.
        if self.template == segment.raw_upper and segment.is_code:
            return True
        return False


class MultiStringParser(BaseParser):
    """An object which matches and returns raw segments on a collection of strings."""

    def __init__(
        self,
        templates: Collection[str],
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        **segment_kwargs,
    ):
        self.templates = {template.upper() for template in templates}
        # Create list version upfront to avoid recreating it multiple times.
        self._simple = frozenset(self.templates)
        super().__init__(
            raw_class=raw_class,
            type=type,
            optional=optional,
            **segment_kwargs,
        )

    def simple(self, parse_context: "ParseContext", crumbs=None):
        """Return simple options for this matcher.

        Because string matchers are not case sensitive we can
        just return the templates here.
        """
        return self._simple, frozenset()

    def _is_first_match(self, segment: BaseSegment):
        """Does the segment provided match according to the current rules."""
        # Is the target a match and IS IT CODE.
        # The latter stops us accidentally matching comments.
        if segment.is_code and segment.raw_upper in self.templates:
            return True
        return False


class RegexParser(BaseParser):
    """An object which matches and returns raw segments based on a regex."""

    def __init__(
        self,
        template: str,
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        anti_template: Optional[str] = None,
        **segment_kwargs,
    ):
        # Store the optional anti-template
        self.template = template
        self.anti_template = anti_template
        # Compile regexes upfront to avoid repeated overhead
        self._anti_template = regex.compile(anti_template or r"", regex.IGNORECASE)
        self._template = regex.compile(template, regex.IGNORECASE)
        super().__init__(
            raw_class=raw_class,
            type=type,
            optional=optional,
            **segment_kwargs,
        )

    def simple(cls, parse_context: ParseContext, crumbs=None):
        """Does this matcher support a uppercase hash matching route?

        Regex segment does NOT for now. We might need to later for efficiency.
        """
        return None

    def _is_first_match(self, segment: BaseSegment):
        """Does the segment provided match according to the current rules.

        RegexParser implements its own matching function where
        we assume that ._template is a r"" string, and is formatted
        for use directly as a regex. This only matches on a single segment.
        """
        if len(segment.raw) == 0:  # pragma: no cover TODO?
            # If it's of zero length it's probably a meta segment.
            # In any case, it won't match here.
            return False
        # Try the regex. Case sensitivity is not supported.
        result = self._template.match(segment.raw_upper)
        if result:
            result_string = result.group(0)
            # Check that we've fully matched
            if result_string == segment.raw_upper:
                # Check that the anti_template (if set) hasn't also matched
                if self.anti_template and self._anti_template.match(segment.raw_upper):
                    return False
                else:
                    return True
        return False
