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

from .segments_base import (BaseSegment, RawSegment, parse_match_logging)
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
    def simple(cls, parse_context):
        """Does this matcher support a uppercase hash matching route?

        The keyword segment DOES, provided that it is not case sensitive,
        we return a tuple in case there is more than one option.
        """
        if not cls._case_sensitive:
            # NB: We go UPPER on make, so no need to convert here
            return (cls._template,)
        return False

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

            parse_match_logging(
                cls.__name__[:10], 'match', 'KW',
                parse_context=parse_context, v_level=4, pattern=cls._template, test=raw_comp, name=cls.__name__)
            if cls._template == raw_comp:
                m = (cls(raw=raw, pos_marker=pos),)  # Return as a tuple
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
    def simple(cls, parse_context):
        """Does this matcher support a uppercase hash matching route?

        Regex segment does NOT for now. We might need to later for efficiency.
        """
        return False

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
        parse_match_logging(
            cls.__name__[:10], 'match', 'RE',
            parse_context=parse_context, v_level=4, pattern=cls._template, test=sc, name=cls.__name__)
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
                    m = (cls(raw=s, pos_marker=segments[0].pos_marker),)  # Return a tuple
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
    def simple(cls, parse_context):
        """Does this matcher support a uppercase hash matching route?

        NamedSegment segment does NOT for now. We might need to later for efficiency.

        There is a way that this *could* be enabled, by allowing *another*
        shortcut route, to look ahead at the names of upcoming segments,
        rather than their content.
        """
        return False

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
            parse_match_logging(
                cls.__name__[:10], 'match', 'NM',
                parse_context=parse_context, v_level=4, pattern=cls._template, test=n, name=cls.__name__)
            if cls._template == n:
                m = (cls(raw=s.raw, pos_marker=segments[0].pos_marker),)  # Return a tuple
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
        # This used to be a problem in python 2. Easier in py3
        f = cls._func
        while True:
            if len(seg_buff) == 0:
                # No buffer to work with
                return MatchResult.from_matched(matched_segs)
            elif f(seg_buff[0]):
                # Got a match
                matched_segs += (seg_buff[0],)
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


class Indent(RawSegment):
    """A segment which is empty but indicates where an indent should be.

    This segment is always empty, i.e. it's raw format is '', but it indicates
    the position of a theoretical indent which will be used in linting
    and reconstruction. Even if there is an *actual indent* that occurs
    in the same place this intentionally *won't* capture it, they will just
    be compared later.
    """

    type = 'indent'
    _is_code = False
    _template = '<unset>'
    _case_sensitive = False
    indent_val = 1
    is_meta = True
    _config_rules = None

    @classmethod
    def when(cls, **kwargs):
        """Configure whether this indent/dedent is available given certain rules.

        All we do is override the _config_rules parameter
        for the class.

        _config_rules should be an iterable of tuples (config, True|False)
        which determine whether this class is enabled or not. Later elements
        override earlier ones.
        """
        if len(kwargs) > 1:
            raise ValueError("More than one condition specified for {0!r}. [{1!r}]".format(
                cls, kwargs))
        # Sorcery (but less to than on KeywordSegment)
        return type(
            cls.__name__,
            (cls, ),
            dict(_config_rules=kwargs)
        )

    @classmethod
    def is_enabled(cls, parse_context):
        """Given a certain parse context, determine if this segment is enabled.

        All rules are assumed to be False if not present in the parse_context,
        and later rules in the config override previous ones.
        """
        # All rules are assumed to be False if not present
        if cls._config_rules is not None:
            config = parse_context.indentation_config or {}
            # This looks like an iteration, but there should only be one.
            for rule, val in cls._config_rules.items():
                conf_val = config.get(rule, False)
                if val == conf_val:
                    return True
                else:
                    return False
        return True

    @staticmethod
    def _suffix():
        """Return any extra output required at the end when logging.

        Meta classess have not much to say here so just stay blank.
        """
        return ""

    @classmethod
    def match(cls, segments, parse_context):
        """This will never be called. If it is then we're using it wrong."""
        raise NotImplementedError(
            "{0} has no match method, it should only be used in a Sequence!".format(
                cls.__name__
            )
        )

    @classmethod
    def expected_string(cls, dialect=None, called_from=None):
        """Return the expected string for this segment."""
        return ''

    def __init__(self, pos_marker):
        """For the indent we override the init method.

        For something without content, the content doesn't make
        sense. The pos_marker, will be matched with the following
        segment, but meta segments are ignored during fixes so it's
        ok in this sense. We need the pos marker later for dealing
        with repairs.
        """
        self._raw = ''
        # TODO: Make sure that we DO actually skip meta segments
        # during fixes.
        self.pos_marker = pos_marker


class Dedent(Indent):
    """A segment which is empty but indicates where an dedent should be.

    This segment is always empty, i.e. it's raw format is '', but it indicates
    the position of a theoretical dedent which will be used in linting
    and reconstruction. Even if there is an *actual dedent* that occurs
    in the same place this intentionally *won't* capture it, they will just
    be compared later.

    """

    indent_val = -1
