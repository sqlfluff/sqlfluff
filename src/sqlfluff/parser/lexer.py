"""The code for the Lexer."""

from collections import namedtuple
import re

from .markers import FilePositionMarker
from .segments_base import RawSegment
from ..errors import SQLLexError


LexMatch = namedtuple('LexMatch', ['new_string', 'new_pos', 'segments'])


class SingletonMatcher(object):
    """This singleton matcher matches single characters.

    This is the simplest usable matcher, but it also defines some of the
    mechanisms for more complicated matchers, which may simply override the
    `_match` function rather than the public `match` function.  This acts as
    the base class for matchers.
    """
    def __init__(self, name, template, target_seg_class, *args, **kwargs):
        self.name = name
        self.template = template
        self.target_seg_class = target_seg_class

    def _match(self, forward_string):
        """The private match function. Just look for a single character match."""
        if forward_string[0] == self.template:
            return forward_string[0]
        else:
            return None

    def match(self, forward_string, start_pos):
        """Given a string, match what we can and return the rest.

        Returns:
            :obj:`LexMatch`

        """
        if len(forward_string) == 0:
            raise ValueError("Unexpected empty string!")
        matched = self._match(forward_string)

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

    @classmethod
    def from_shorthand(cls, name, template, **kwargs):
        """A shorthand was of making new instances of this class.

        This is the primary way of defining matchers. It is convenient
        because several parameters of the matcher and the class of segment
        to be returned are shared, and here we define both together.
        """
        return cls(
            name, template,
            RawSegment.make(
                template, name=name, **kwargs
            )
        )


class RegexMatcher(SingletonMatcher):
    """This RegexMatcher matches based on regular expressions."""

    def __init__(self, *args, **kwargs):
        super(RegexMatcher, self).__init__(*args, **kwargs)
        # We might want to configure this at some point, but for now, newlines
        # do get matched by .
        flags = re.DOTALL
        self._compiled_regex = re.compile(self.template, flags)

    def _match(self, forward_string):
        """Use regexes to match chunks."""
        match = self._compiled_regex.match(forward_string)
        if match:
            return match.group(0)
        else:
            return None


class RepeatedMultiMatcher(SingletonMatcher):
    """Uses other matchers in priority order.

    Args:
        *submatchers: An iterable of other matchers which can be tried
            in turn. If none match a given forward looking string we simply
            return the unmatched part as per any other matcher.

    """

    def __init__(self, *submatchers):
        self.submatchers = submatchers

    def match(self, forward_string, start_pos):
        """Iteratively match strings using the selection of submatchers."""
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

    @classmethod
    def from_struct(cls, s):
        """Creates a matcher from a lexer_struct.

        Expects an iterable of :obj:`tuple`. Each tuple should be:
        (name, type, pattern, kwargs).

        """
        matchers = []
        for elem in s:
            if elem[1] == "regex":
                m_cls = RegexMatcher
            elif elem[1] == "singleton":
                m_cls = SingletonMatcher
            else:
                raise ValueError(
                    "Unexpected matcher type in lexer struct: {0!r}".format(
                        elem[1]))
            k = elem[3] or {}
            m = m_cls.from_shorthand(elem[0], elem[2], **k)
            matchers.append(m)
        return cls(*matchers)


lexer_struct = [
    # name, type, pattern, kwargs
    ("whitespace", "regex", r"[\t ]*", None),
    ("inline_comment", "regex", r"(-- |#)[^\n]*", dict(is_comment=True)),
    ("block_comment", "regex", r"\/\*([^\*]|\*[^\/])*\*\/", dict(is_comment=True)),
    ("single_quote", "regex", r"'[^']*'", dict(is_code=True)),
    ("double_quote", "regex", r'"[^"]*"', dict(is_code=True)),
    ("back_quote", "regex", r"`[^`]*`", dict(is_code=True)),
    ("numeric_literal", "regex", r"([0-9]+(\.[0-9]+)?)", dict(is_code=True)),
    ("greater_than_or_equal", "regex", r">=", dict(is_code=True)),
    ("less_than_or_equal", "regex", r"<=", dict(is_code=True)),
    ("newline", "regex", r"\r\n", None),
    ("casting_operator", "regex", r"::", dict(is_code=True)),
    ("not_equals", "regex", r"!=", dict(is_code=True)),
    ("newline", "singleton", "\n", None),
    ("equals", "singleton", "=", dict(is_code=True)),
    ("greater_than", "singleton", ">", dict(is_code=True)),
    ("less_than", "singleton", "<", dict(is_code=True)),
    ("dot", "singleton", ".", dict(is_code=True)),
    ("comma", "singleton", ",", dict(is_code=True)),
    ("plus", "singleton", "+", dict(is_code=True)),
    ("tilde", "singleton", "~", dict(is_code=True)),
    ("minus", "singleton", "-", dict(is_code=True)),
    ("divide", "singleton", "/", dict(is_code=True)),
    ("star", "singleton", "*", dict(is_code=True)),
    ("bracket_open", "singleton", "(", dict(is_code=True)),
    ("bracket_close", "singleton", ")", dict(is_code=True)),
    ("semicolon", "singleton", ";", dict(is_code=True)),
    ("code", "regex", r"[0-9a-zA-Z_]*", dict(is_code=True))
]


class Lexer(object):
    """The Lexer class actually does the lexing step.

    This class is likely called directly from a top level segment
    such as the `FileSegment`.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.matcher = RepeatedMultiMatcher.from_struct(lexer_struct)

    def lex(self, raw):
        """Take a string and return segments.

        If we fail to match the *whole* string, then we must have
        found something that we cannot lex. This should raise a
        `SQLLexError`, which we expect will be caught by whichever
        CLI command launched this.
        """
        start_pos = FilePositionMarker.from_fresh()
        res = self.matcher.match(raw, start_pos)
        if len(res.new_string) > 0:
            raise SQLLexError(
                "Unable to lex characters: '{0!r}...'".format(
                    res.new_string[:10]),
                pos=res.new_pos
            )
        return res.segments
