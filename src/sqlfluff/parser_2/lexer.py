""" The code for the new lexer """

from collections import namedtuple

# from .markers import FilePositionMarker
# from .segments_base import RawSegment


LexMatch = namedtuple('LexMatch', ['new_string', 'new_pos', 'segments'])


class BaseForwardMatcher(object):
    def match(self, forward_string, start_pos):
        # match should return the remainder of the forward
        # string, the new pos of that string and a list
        # of segments.
        raise NotImplementedError(
            "{0} has no match function implmeneted".format(
                self.__class__.__name__))


class SingletonMatcher(BaseForwardMatcher):
    def __init__(self, name, template, target_seg_class):
        self.name = name
        self.template = template
        self.target_seg_class = target_seg_class

    def match(self, forward_string, start_pos):
        if len(forward_string) == 0:
            raise ValueError("Unexpected empty string!")
        raw = forward_string[0]
        if raw == self.template:
            new_pos = start_pos.advance_by(raw)
            return LexMatch(
                forward_string[1:],
                new_pos,
                tuple([
                    self.target_seg_class(
                        raw=raw,
                        pos_marker=start_pos),
                ])
            )
        else:
            return LexMatch(forward_string, start_pos, tuple())


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


default_config = {}


class Lexer(object):
    def __init__(self, config=None):
        self.config = config or default_config

    def lex(self, raw):
        return []
