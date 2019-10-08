"""
Common Segment Definitions

Here we define:
- KeywordSegment
- ReSegment

These depend on the base segments, and extend them
for some more useful use cases. The intent here is that
these segments have meaning regardless of what dialect
we use, and will be common between all of them.
"""

import logging
import re

from .segments_base import (BaseSegment, RawSegment)
from .match import MatchResult


class KeywordSegment(RawSegment):
    """ The Keyword Segment is a bit special, because while it
    can be instantiated directly, we mostly generate them on the
    fly for convenience. The `make` method is defined on RawSegment
    instead of here, but can be used here too. """

    type = 'keyword'
    _is_code = True
    _template = '<unset>'
    _case_sensitive = False

    @classmethod
    def match(cls, segments, match_depth=0, parse_depth=0, verbosity=0):
        """ Keyword implements it's own matching function """
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # We're only going to match against the first element
        if len(segments) >= 1:
            raw = segments[0].raw
            pos = segments[0].pos_marker
            if cls._case_sensitive:
                raw_comp = raw
            else:
                raw_comp = raw.upper()
            logging.debug("[PD:{0} MD:{1}] (KW) {2}.match considering {3!r} against {4!r}".format(
                parse_depth, match_depth, cls.__name__, raw_comp, cls._template))
            if cls._template == raw_comp:
                m = cls(raw=raw, pos_marker=pos),  # Return as a tuple
                return MatchResult(m, segments[1:])
        else:
            logging.debug("{1} will not match sequence of length {0}".format(len(segments), cls.__name__))
        return MatchResult.from_unmatched(segments)

    @classmethod
    def expected_string(cls):
        return cls._template


class ReSegment(KeywordSegment):
    """ A more flexible matching segment for use of regexes
    USE WISELY """
    @classmethod
    def match(cls, segments, match_depth=0, parse_depth=0, verbosity=0):
        """ ReSegment implements it's own matching function,
        we assume that ._template is a r"" string, and is formatted
        for use directly as a regex. This only matches on a single segment."""
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]
        # Regardless of what we're passed, make a string.
        # NB: We only match on the first element of a set of segments.
        s = segments[0].raw
        # Deal with case sentitivity
        if not cls._case_sensitive:
            sc = s.upper()
        else:
            sc = s
        if len(s) == 0:
            raise ValueError("Zero length string passed to ReSegment!?")
        logging.debug("[PD:{0} MD:{1}] (RE) {2}.match considering {3!r} against {4!r}".format(
            parse_depth, match_depth, cls.__name__, sc, cls._template))
        # Try the regex
        result = re.match(cls._template, sc)
        if result:
            r = result.group(0)
            # Check that we've fully matched
            if r == sc:
                m = cls(raw=s, pos_marker=segments[0].pos_marker),  # Return a tuple
                return MatchResult(m, segments[1:])
        return MatchResult.from_unmatched(segments)

    @classmethod
    def expected_string(cls):
        return cls.type


class NamedSegment(KeywordSegment):
    """ A segment which matches based on the `name` property
    of segments. Useful for matching quoted segments.
    USE WISELY """
    @classmethod
    def match(cls, segments, match_depth=0, parse_depth=0, verbosity=0):
        """ NamedSegment implements it's own matching function,
        we assume that ._template is the `name` of a segment"""
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # We only match on the first element of a set of segments
        if len(segments) >= 1:
            s = segments[0]
            if not cls._case_sensitive:
                n = s.name.upper()
            else:
                n = s.name
            logging.debug("[PD:{0} MD:{1}] (KW) {2}.match considering {3!r} against {4!r}".format(
                parse_depth, match_depth, cls.__name__, n, cls._template))
            if cls._template == n:
                m = cls(raw=s.raw, pos_marker=segments[0].pos_marker),  # Return a tuple
                return MatchResult(m, segments[1:])
        else:
            logging.debug("{1} will not match sequence of length {0}".format(len(segments), cls.__name__))
        return MatchResult.from_unmatched(segments)

    @classmethod
    def expected_string(cls):
        return "[" + cls._template + "]"
