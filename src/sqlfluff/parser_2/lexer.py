""" The code for the new lexer """

from collections import namedtuple
import re

from .markers import FilePositionMarker
from .segments_base import RawSegment
from ..errors import SQLParseError


LexMatch = namedtuple('LexMatch', ['new_string', 'new_pos', 'segments'])


class BaseForwardMatcher(object):
    def __init__(self, name, template, target_seg_class, *args, **kwargs):
        self.name = name
        self.template = template
        self.target_seg_class = target_seg_class

    def match(self, forward_string, start_pos):
        # match should return the remainder of the forward
        # string, the new pos of that string and a list
        # of segments.
        raise NotImplementedError(
            "{0} has no match function implmeneted".format(
                self.__class__.__name__))

    @classmethod
    def from_shorthand(cls, name, template, **kwargs):
        return cls(
            name, template,
            RawSegment.make(
                template, name=name, **kwargs
            )
        )


class SingletonMatcher(BaseForwardMatcher):
    def _match(self, forward_string):
        if forward_string[0] == self.template:
            return forward_string[0]
        else:
            return None

    def match(self, forward_string, start_pos):
        if len(forward_string) == 0:
            raise ValueError("Unexpected empty string!")
        matched = self._match(forward_string)
        # logging.debug("Matcher: {0} - {1}".format(forward_string, matched))
        if matched:
            new_pos = start_pos.advance_by(matched)
            return LexMatch(
                forward_string[len(matched):],
                new_pos,
                tuple([
                    self.target_seg_class(
                        raw=matched,
                        pos_marker=start_pos),
                ])
            )
        else:
            return LexMatch(forward_string, start_pos, tuple())


class RegexMatcher(SingletonMatcher):
    def __init__(self, *args, **kwargs):
        super(RegexMatcher, self).__init__(*args, **kwargs)
        # We might want to configure this at some point, but for now, newlines
        # do get matched by .
        flags = re.DOTALL
        self._compiled_regex = re.compile(self.template, flags)

    """ Use regexes to match chunks """
    def _match(self, forward_string):
        match = self._compiled_regex.match(forward_string)
        if match:
            return match.group(0)
        else:
            return None


class StatefulMatcher(BaseForwardMatcher):
    """
    has a start and an end (if no start or end, then picks up the remainder)
    contains potentially other matchers
    is optionally flat or nested [maybe?] - probably just flat to start with

    stateful matcher if matching the start, will take hold and consume until it ends
    """

    # NB the base matcher is probably stateful, in the `code` state, but will end up
    # using the remainder segment liberally.
    def __init__(self, name, submatchers, remainder_segment):
        self.name = name  # The name of the state
        self.submatchers = submatchers or []  # Could be empty?
        self.remainder_segment = remainder_segment  # Required


class RepeatedMultiMatcher(BaseForwardMatcher):
    """
    Uses other matchers in priority order
    """

    # NB the base matcher is probably stateful, in the `code` state, but will end up
    # using the remainder segment liberally.
    def __init__(self, *submatchers):
        self.submatchers = submatchers
        # If we bottom out then return the rest of the string

    def match(self, forward_string, start_pos):
        seg_buff = tuple()
        while True:
            if len(forward_string) == 0:
                return LexMatch(
                    forward_string,
                    start_pos,
                    seg_buff
                )
            for matcher in self.submatchers:
                res = matcher.match(forward_string, start_pos)
                if res.segments:
                    # If we have new segments then whoop!
                    seg_buff += res.segments
                    forward_string = res.new_string
                    start_pos = res.new_pos
                    # Cycle back around again and start with the top
                    # matcher again.
                    break
                else:
                    continue
            else:
                # We've got so far, but now can't match. Return
                return LexMatch(
                    forward_string,
                    start_pos,
                    seg_buff
                )


default_config = {}


class Lexer(object):
    def __init__(self, config=None):
        self.config = config or default_config
        self.matcher = RepeatedMultiMatcher(
            RegexMatcher.from_shorthand("whitespace", r"[\t ]*"),
            RegexMatcher.from_shorthand("inline_comment", r"(-- |#)[^\n]*"),
            RegexMatcher.from_shorthand("block_comment", r"/\*([^\\]|\\[^\*])*"),
            RegexMatcher.from_shorthand("single_quote", r"'[^']*'", is_code=True),
            RegexMatcher.from_shorthand("double_quote", r'"[^"]*"', is_code=True),
            RegexMatcher.from_shorthand("back_quote", r"`[^`]*`", is_code=True),
            SingletonMatcher.from_shorthand("newline", "\n"),
            SingletonMatcher.from_shorthand("equals", "=", is_code=True),
            SingletonMatcher.from_shorthand("dot", ".", is_code=True),
            SingletonMatcher.from_shorthand("comma", ",", is_code=True),
            SingletonMatcher.from_shorthand("plus", "+", is_code=True),
            SingletonMatcher.from_shorthand("minus", "-", is_code=True),
            SingletonMatcher.from_shorthand("divide", "/", is_code=True),
            SingletonMatcher.from_shorthand("star", "*", is_code=True),
            SingletonMatcher.from_shorthand("bracket_open", "(", is_code=True),
            SingletonMatcher.from_shorthand("bracket_close", ")", is_code=True),
            SingletonMatcher.from_shorthand("semicolon", ";", is_code=True),
            RegexMatcher.from_shorthand("code", r"[0-9a-zA-Z_]*", is_code=True)
        )

    def lex(self, raw):
        start_pos = FilePositionMarker.from_fresh()
        res = self.matcher.match(raw, start_pos)
        if len(res.new_string) > 0:
            raise SQLParseError(
                "Unable to lex characters: '{0}...'".format(
                    res.new_string[:10]))
        return res.segments
