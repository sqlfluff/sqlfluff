"""Common Segment Definitions.

Here we define:
- KeywordSegment
- SymbolSegment
- ReSegment

These depend on the base segments, and extend them
for some more useful use cases. The intent here is that
these segments have meaning regardless of what dialect
we use, and will be common between all of them.
"""

import re
from typing import Optional, List

from sqlfluff.core.parser.match_result import MatchResult
from sqlfluff.core.parser.match_wrapper import match_wrapper
from sqlfluff.core.parser.context import ParseContext

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import RawSegment


class _ProtoKeywordSegment(RawSegment):
    """A segment used for matching single words or entities.

    The _ProtoKeywordSegment Segment is a bit special, because while it
    can be instantiated directly, we mostly generate them on the
    fly for convenience. The `make` method is defined on RawSegment
    instead of here, but can be used here too.

    This is distinct from KeywordSegment so that we can inherit
    from this class (which mostly provides common functionality)
    without inheriting the type `keyword` which rules and modules
    may depend on later.
    """

    type = "_proto_keyword"
    _is_code = True
    _template = "<unset>"

    @classmethod
    def simple(cls, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        The keyword segment DOES, provided that it is not case sensitive,
        we return a tuple in case there is more than one option.
        """
        # NB: We go UPPER on make, so no need to convert here
        return [cls._template]

    @classmethod
    @match_wrapper(v_level=4)
    def match(cls, segments, parse_context):
        """Compare input segments for a match, return a `MatchResult`.

        Note: For Keyword matching, we only consider the *first* element,
        because we assume that a keyword can only span one raw segment.
        """
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # We're only going to match against the first element
        if len(segments) >= 1:
            raw = segments[0].raw
            pos = segments[0].pos_marker
            raw_comp = raw.upper()

            # Is the target a match and IS IT CODE.
            # The latter stops us accidentally matching comments.
            if cls._template == raw_comp and segments[0].is_code:
                m = (cls(raw=raw, pos_marker=pos),)  # Return as a tuple
                return MatchResult(m, segments[1:])
        return MatchResult.from_unmatched(segments)


class KeywordSegment(_ProtoKeywordSegment):
    """A segment used for matching single words.

    We rename the segment class here so that descendants of
    _ProtoKeywordSegment can use the same functionality
    but don't end up being labelled as a `keyword` later.
    """

    type = "keyword"


class SymbolSegment(_ProtoKeywordSegment):
    """A segment used for matching single entities which aren't keywords.

    We rename the segment class here so that descendants of
    _ProtoKeywordSegment can use the same functionality
    but don't end up being labelled as a `keyword` later.
    """

    type = "symbol"


class ReSegment(_ProtoKeywordSegment):
    """A more flexible matching segment which uses of regexes.

    This is more flexible that the `_ProtoKeywordSegment` but also more complicated
    and so the `_ProtoKeywordSegment` should be used instead wherever possible.
    """

    _anti_template = None
    """If `_anti_template` is set, then we exclude anything that matches it."""

    @classmethod
    def simple(cls, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        Regex segment does NOT for now. We might need to later for efficiency.
        """
        return None

    @classmethod
    @match_wrapper(v_level=4)
    def match(cls, segments, parse_context):
        """Compare input segments for a match, return a `MatchResult`.

        ReSegment implements its own matching function where
        we assume that ._template is a r"" string, and is formatted
        for use directly as a regex. This only matches on a single segment.
        """
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]
        # Regardless of what we're passed, make a string.
        # NB: We only match on the first element of a set of segments.
        s = segments[0].raw
        # Case sensitivity is not supported
        sc = s.upper()
        if len(s) == 0:
            raise ValueError("Zero length string passed to ReSegment!?")
        # Try the regex
        result = re.match(cls._template, sc)
        if result:
            r = result.group(0)
            # Check that we've fully matched
            if r == sc:
                # Check that the _anti_template (if set) hasn't also matched
                if cls._anti_template and re.match(cls._anti_template, sc):
                    return MatchResult.from_unmatched(segments)
                else:
                    m = (
                        cls(raw=s, pos_marker=segments[0].pos_marker),
                    )  # Return a tuple
                    return MatchResult(m, segments[1:])
        return MatchResult.from_unmatched(segments)


class NamedSegment(_ProtoKeywordSegment):
    """A segment which matches based on the `name` property of segments.

    Useful for matching quoted segments, or anything else which
    is largely identified by the Lexer.
    """

    @classmethod
    def simple(cls, parse_context: ParseContext) -> Optional[List[str]]:
        """Does this matcher support a uppercase hash matching route?

        NamedSegment segment does NOT for now. We might need to later for efficiency.

        There is a way that this *could* be enabled, by allowing *another*
        shortcut route, to look ahead at the names of upcoming segments,
        rather than their content.
        """
        return None

    @classmethod
    @match_wrapper(v_level=4)
    def match(cls, segments, parse_context):
        """Compare input segments for a match, return a `MatchResult`.

        NamedSegment implements its own matching function where
        we assume that ._template is the `name` of a segment.
        """
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # We only match on the first element of a set of segments
        if len(segments) >= 1:
            s = segments[0]
            # Case sensitivity is not supported.
            n = s.name.upper()
            if cls._template == n:
                m = (
                    cls(raw=s.raw, pos_marker=segments[0].pos_marker),
                )  # Return a tuple
                return MatchResult(m, segments[1:])
        return MatchResult.from_unmatched(segments)
