"""Individual segment parsers.

Matchable objects which return individual segments.
"""

from abc import abstractmethod
from typing import Any, Collection, Dict, Optional, Sequence, Tuple, Type
from uuid import uuid4

import regex

from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.matchable import Matchable
from sqlfluff.core.parser.segments import BaseSegment, RawSegment
from sqlfluff.core.parser.types import SimpleHintType


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
        # The following kwargs are passed on to the segment:
        trim_chars: Optional[Tuple[str, ...]] = None,
    ) -> None:
        self.raw_class = raw_class
        # Store instance_types rather than just type to allow
        # for multiple possible types to be supported in derivative
        # classes.
        self._instance_types: Tuple[str, ...] = (type or raw_class.type,)
        self.optional = optional
        self._trim_chars = trim_chars
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

    def _match_at(self, idx: int) -> MatchResult:
        """Construct a MatchResult at a given index.

        This is a helper function for reuse by other parsers.
        """
        segment_kwargs: Dict[str, Any] = {}
        if self._instance_types:
            segment_kwargs["instance_types"] = self._instance_types
        if self._trim_chars:
            segment_kwargs["trim_chars"] = self._trim_chars
        return MatchResult(
            matched_slice=slice(idx, idx + 1),
            matched_class=self.raw_class,
            segment_kwargs=segment_kwargs,
        )


class TypedParser(BaseParser):
    """An object which matches and returns raw segments based on types."""

    def __init__(
        self,
        template: str,
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        trim_chars: Optional[Tuple[str, ...]] = None,
    ) -> None:
        """Initialize a new instance of the class.

        Args:
            template (str): The template type.
            raw_class (Type[RawSegment]): The raw segment class.
            type (Optional[str]): The type of the instance.
            optional (bool): Whether the instance is optional.
            trim_chars (Optional[Tuple[str, ...]]): The characters to trim.

        Returns:
            None
        """
        # NB: the template in this case is the _target_ type.
        # The type kwarg is the eventual type.
        self.template = template
        # Pre-calculate the appropriate frozenset for matching later.
        self._target_types = frozenset((template,))
        super().__init__(
            raw_class=raw_class,
            optional=optional,
            trim_chars=trim_chars,
        )
        # NOTE: We override the instance types after initialising the base
        # class. We want to ensure that re-matching is possible by ensuring that
        # the `type` pre-matching is still present post-match even if it's not
        # part of the natural type hierarchy for the new `raw_class`.
        # The new `type` becomes the "primary" type, but the template will still
        # be part of the resulting `class_types`.
        # We do this here rather than in the base class to keep the dialect-facing
        # API the same.
        self._instance_types: Tuple[str, ...] = ()
        # Primary type if set.
        if type is not None:
            self._instance_types += (type,)
        # New root types
        if type != raw_class.type:
            self._instance_types += (raw_class.type,)
        # Template type (if it's not in the subclasses of the raw_class).
        if not raw_class.class_is_type(template):
            self._instance_types += (template,)

    def __repr__(self) -> str:
        """Return a string representation of the TypedParser object."""
        return f"<TypedParser: {self.template!r}>"

    def simple(
        self, parse_context: ParseContext, crumbs: Optional[Tuple[str, ...]] = None
    ) -> SimpleHintType:
        """Check if the matcher supports uppercase hash matching route.

        The TypedParser segment does not support matching against raw strings,
        but it does support matching against types. Matching is done against both the
        template and the resulting type, to support re-matching.

        Args:
            parse_context (ParseContext): The parse context.
            crumbs (Optional[Tuple[str, ...]], optional): The crumbs.
            Defaults to None.

        Returns:
            SimpleHintType: A set of target types.
        """
        return frozenset(), self._target_types

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match against this matcher."""
        if segments[idx].is_type(self.template):
            return self._match_at(idx)
        return MatchResult.empty_at(idx)


class StringParser(BaseParser):
    """An object which matches and returns raw segments based on strings."""

    def __init__(
        self,
        template: str,
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        trim_chars: Optional[Tuple[str, ...]] = None,
    ):
        self.template = template.upper()
        # Create list version upfront to avoid recreating it multiple times.
        self._simple = frozenset((self.template,))
        super().__init__(
            raw_class=raw_class,
            type=type,
            optional=optional,
            trim_chars=trim_chars,
        )

    def __repr__(self) -> str:
        return f"<StringParser: {self.template!r}>"

    def simple(
        self, parse_context: "ParseContext", crumbs: Optional[Tuple[str, ...]] = None
    ) -> SimpleHintType:
        """Return simple options for this matcher.

        Because string matchers are not case sensitive we can
        just return the template here.
        """
        return self._simple, frozenset()

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match against this matcher.

        NOTE: We check that the segment is also code to avoid matching
        unexpected comments.
        """
        if segments[idx].raw_upper == self.template and segments[idx].is_code:
            return self._match_at(idx)
        return MatchResult.empty_at(idx)


class MultiStringParser(BaseParser):
    """An object which matches and returns raw segments on a collection of strings."""

    def __init__(
        self,
        templates: Collection[str],
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        trim_chars: Optional[Tuple[str, ...]] = None,
    ):
        self.templates = {template.upper() for template in templates}
        # Create list version upfront to avoid recreating it multiple times.
        self._simple = frozenset(self.templates)
        super().__init__(
            raw_class=raw_class,
            type=type,
            optional=optional,
            trim_chars=trim_chars,
        )

    def __repr__(self) -> str:
        return f"<MultiStringParser: {self.templates!r}>"

    def simple(
        self, parse_context: "ParseContext", crumbs: Optional[Tuple[str, ...]] = None
    ) -> SimpleHintType:
        """Return simple options for this matcher.

        Because string matchers are not case sensitive we can
        just return the templates here.
        """
        return self._simple, frozenset()

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match against this matcher.

        NOTE: We check that the segment is also code to avoid matching
        unexpected comments.
        """
        if segments[idx].is_code and segments[idx].raw_upper in self.templates:
            return self._match_at(idx)
        return MatchResult.empty_at(idx)


class RegexParser(BaseParser):
    """An object which matches and returns raw segments based on a regex."""

    def __init__(
        self,
        template: str,
        raw_class: Type[RawSegment],
        type: Optional[str] = None,
        optional: bool = False,
        anti_template: Optional[str] = None,
        trim_chars: Optional[Tuple[str, ...]] = None,
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
            trim_chars=trim_chars,
        )

    def __repr__(self) -> str:
        return f"<RegexParser: {self.template!r}>"

    def simple(
        cls, parse_context: ParseContext, crumbs: Optional[Tuple[str, ...]] = None
    ) -> None:
        """Does this matcher support a uppercase hash matching route?

        Regex segment does NOT for now. We might need to later for efficiency.
        """
        return None

    def match(
        self,
        segments: Sequence["BaseSegment"],
        idx: int,
        parse_context: "ParseContext",
    ) -> MatchResult:
        """Match against this matcher.

        NOTE: This method uses .raw_upper and so case sensitivity is
        not supported.
        """
        _raw = segments[idx].raw_upper
        result = self._template.match(_raw)
        if result:
            result_string = result.group(0)
            # Check that we've fully matched
            if result_string == _raw:
                # Check that the anti_template (if set) hasn't also matched
                if not self.anti_template or not self._anti_template.match(_raw):
                    return self._match_at(idx)
        return MatchResult.empty_at(idx)
