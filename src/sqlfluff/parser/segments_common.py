"""Common Segment Definitions.

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
import six

from .segments_base import (BaseSegment, RawSegment)
from .match import MatchResult


class KeywordSegment(RawSegment):
    """A segment used for matching single words or entities.

    The Keyword Segment is a bit special, because while it
    can be instantiated directly, we mostly generate them on the
    fly for convenience. The `make` method is defined on RawSegment
    instead of here, but can be used here too.
    """

    type = 'keyword'
    _is_code = True
    _template = '<unset>'
    _case_sensitive = False

    @classmethod
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
            if cls._case_sensitive:
                raw_comp = raw
            else:
                raw_comp = raw.upper()
            logging.debug("[PD:{0} MD:{1}] (KW) {2}.match considering {3!r} against {4!r}".format(
                parse_context.parse_depth, parse_context.match_depth, cls.__name__, raw_comp, cls._template))
            if cls._template == raw_comp:
                m = cls(raw=raw, pos_marker=pos),  # Return as a tuple
                return MatchResult(m, segments[1:])
        else:
            logging.debug("{1} will not match sequence of length {0}".format(len(segments), cls.__name__))
        return MatchResult.from_unmatched(segments)

    @classmethod
    def expected_string(cls, dialect=None, called_from=None):
        """Return the expected string for this segment."""
        return cls._template


class ReSegment(KeywordSegment):
    """A more flexible matching segment which uses of regexes.

    This is more flexible that the `KeywordSegment` but also more complicated
    and so the `KeywordSegment` should be used instead wherever possible.
    """

    _anti_template = None
    """If `_anti_template` is set, then we exclude anything that matches it."""

    @classmethod
    def match(cls, segments, parse_context):
        """Compare input segments for a match, return a `MatchResult`.

        ReSegment implements it's own matching function where
        we assume that ._template is a r"" string, and is formatted
        for use directly as a regex. This only matches on a single segment.
        """
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
            parse_context.parse_depth, parse_context.match_depth, cls.__name__, sc, cls._template))
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
                    m = cls(raw=s, pos_marker=segments[0].pos_marker),  # Return a tuple
                    return MatchResult(m, segments[1:])
        return MatchResult.from_unmatched(segments)

    @classmethod
    def expected_string(cls, dialect=None, called_from=None):
        """Return the expected string for this segment."""
        return cls.type


class NamedSegment(KeywordSegment):
    """A segment which matches based on the `name` property of segments.

    Useful for matching quoted segments, or anything else which
    is largely identified by the Lexer.
    """
    @classmethod
    def match(cls, segments, parse_context):
        """Compare input segments for a match, return a `MatchResult`.

        NamedSegment implements it's own matching function where
        we assume that ._template is the `name` of a segment.
        """
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
                parse_context.parse_depth, parse_context.match_depth, cls.__name__, n, cls._template))
            if cls._template == n:
                m = cls(raw=s.raw, pos_marker=segments[0].pos_marker),  # Return a tuple
                return MatchResult(m, segments[1:])
        else:
            logging.debug("{1} will not match sequence of length {0}".format(len(segments), cls.__name__))
        return MatchResult.from_unmatched(segments)

    @classmethod
    def expected_string(cls, dialect=None, called_from=None):
        """Return the expected string for this segment."""
        return "[" + cls._template + "]"


class LambdaSegment(BaseSegment):
    """A segment which when the given lambda is applied to it returns true.

    This is one of the more abstract segments, and which could be used to
    implement version of most of the other kinds of segments indirectly.

    It is also the most complicated and the most abstract and so should be
    used thoughtfully.
    """

    @classmethod
    def match(cls, segments, parse_context):
        """Compare input segments for a match, return a `MatchResult`.

        NamedSegment implements it's own matching function,
        we assume that ._template is a function.
        """
        # If we've been passed the singular, make it a list
        if isinstance(segments, BaseSegment):
            segments = [segments]

        # We match as many of these as we can.
        seg_buff = segments
        matched_segs = ()
        # We need to do a bit of python2/3 munging here.
        f = six.get_unbound_function(cls._func)
        while True:
            if len(seg_buff) == 0:
                # No buffer to work with
                return MatchResult.from_matched(matched_segs)
            elif f(seg_buff[0]):
                # Got a match
                matched_segs += seg_buff[0],
                seg_buff = seg_buff[1:]
            else:
                # Got buffer but no match
                return MatchResult(matched_segs, seg_buff)

    @classmethod
    def expected_string(cls, dialect=None, called_from=None):
        """Return the expected string for this segment."""
        return "!!TODO!!"

    @classmethod
    def make(cls, func, name, **kwargs):
        """Make a subclass of the segment using a method.

        Note: This requires a custom make method, because it's a bit different.
        """
        # Now lets make the classname (it indicates the mother class for clarity)
        classname = "{0}_{1}".format(name, cls.__name__)
        # This is the magic, we generate a new class! SORCERY
        newclass = type(classname, (cls, ),
                        dict(_func=func, _name=name, **kwargs))
        # Now we return that class in the abstract. NOT INSTANTIATED
        return newclass
