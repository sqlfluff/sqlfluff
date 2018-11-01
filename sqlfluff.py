""" The Main file for SQLFluff """

import click
# import os
import re
from collections import namedtuple


def ordinalise(s):
    return [ord(c) for c in s]


# chunks should be immutable, they are a subclass of namedtuple (context defaults to None)
class PositionedChunk(namedtuple('ProtoChunk', ['chunk', 'start_pos', 'line_no', 'context'])):
    __slots__ = ()

    def __len__(self):
        return len(self.chunk)

    def contextualise(self, context):
        # Return a copy, just with the context set
        return PositionedChunk(self.chunk, self.start_pos, self.line_no, context=context)

    def split_at(self, pos):
        if self.context:
            raise RuntimeError("Attempting to split a chunk which already has context!")
        if pos <= 0 or pos > len(self):
            raise RuntimeError("Trying to split at wrong index: {pos}".format(pos=pos))
        return (
            PositionedChunk(self.chunk[:pos], self.start_pos, self.line_no, None),
            PositionedChunk(self.chunk[pos:], self.start_pos + pos, self.line_no, None))

    def subchunk(self, start, end=None, context=None):
        if end:
            return PositionedChunk(
                self.chunk[start: end], self.start_pos + start,
                self.line_no, context=context or self.context)
        else:
            return PositionedChunk(
                self.chunk[start:], self.start_pos + start,
                self.line_no, context=context or self.context)


class ChunkString(object):
    def __init__(self, *args):
        assert all([isinstance(elem, PositionedChunk) for elem in args])
        self.chunk_list = list(args)

    def __add__(self, other):
        return ChunkString(*self.chunk_list, *other.chunk_list)

    def __getitem__(self, key):
        return self.chunk_list[key]

    def __len__(self):
        return len(self.chunk_list)

    def content_list(self):
        return [elem.content for elem in self.chunk_list]


class CharMatchPattern(object):
    """ Intended for things like quote characters """
    def __init__(self, c, name):
        self._char = c
        self.name = name

    def _repr_pattern(self):
        return self._char * 2

    def __repr__(self):
        return "<{classname}: '{pattern}'>".format(classname=self.__class__.__name__, pattern=self._repr_pattern())

    def first_match_pos(self, s):
        # Assume s is a string
        for idx, c in enumerate(s):
            if c == self._char:
                return idx
        else:
            return None

    def span(self, s):
        # SPAN should return the index from and to of the match
        # a single character match will have a difference of span
        # equal to 1.
        first = self.first_match_pos(s)
        # check that we're not matching in the last position
        # (otherwise we can't add one to it)
        if first is not None and first < len(s):
            # Look or the next match after this
            second = self.first_match_pos(s[first + 1:])
            if second:
                # we add one here because we add it above
                return first, second + 2 + first
        # unless both first AND second match, then return here
        return first, None

    def chunkmatch(self, c):
        """ Given a full chunk, rather than just a string, return the first matching subchunk """
        span = self.span(c.chunk)
        if span[0] is not None:
            # there's a start!
            if span[1] is not None:
                # there's a defined end!
                return c.subchunk(start=span[0], end=span[1], context='match')
            else:
                # start but no end
                return c.subchunk(start=span[0], context='match')
        else:
            return None


class RegexMatchPattern(CharMatchPattern):
    def __init__(self, r, name):
        self._pattern = re.compile(r)
        self.name = name

    def _repr_pattern(self):
        return self._pattern.pattern

    def span(self, s):
        # Assume s is a string
        m = self._pattern.search(s)
        if m:
            return m.span()
        else:
            return None, None

    def first_match_pos(self, s):
        span = self.span(s)
        return span[0]


class MatcherBag(object):
    def __init__(self, *matchers):
        expanded_matchers = []
        for elem in matchers:
            if isinstance(elem, MatcherBag):
                expanded_matchers += elem._matchers
            elif isinstance(elem, CharMatchPattern):
                # matches any match pattern or derivative
                expanded_matchers.append(elem)
            else:
                raise TypeError("Unexpected Class in Bag: {0}".format(elem))
        # Check that names are unique
        assert len(expanded_matchers) == len(set([elem.name for elem in expanded_matchers]))
        # store them as a dict, so we can do lookups
        self._matchers = expanded_matchers

    def __add__(self, other):
        # combining bags is just like making a bag with the combination of the matchers.
        # there will be a uniqueness check in this operation
        return MatcherBag(*self._matchers, *other._matchers)
    
    def __len__(self):
        return len(self._matchers)

    def chunkmatch(self, c):
        """
        Given a full chunk, compare against matchers in the bag and then order by first match

        Return a list of tuples (subchunk, pos, matcher)
        """
        match_buffer = []
        for matcher in self._matchers:
            chk = matcher.chunkmatch(c)
            if chk:
                match_buffer.append((chk, chk.start_pos - c.start_pos, matcher))
        return sorted(match_buffer, key=lambda x: x[1])


class AnsiSQLDialiect(object):
    # Whitespace is what divides other bits of syntax
    whitespace_regex = RegexMatchPattern(r'\s+', 'whitespace')
    # Anything after an inline comment gets chunked together as not code
    inline_comment_regex = RegexMatchPattern(r'(--|#)[^\n]*', 'comment')  # In MySQL, we need a space after the '--'
    # Anything between the first and last part of this tuple counts as not code
    closed_block_comment = RegexMatchPattern(r'/\*[^\n]*\*/', 'closed_block_comment')
    open_block_comment_start = RegexMatchPattern(r'/\*[^\n]', 'open_block_comment_start')
    open_block_comment_end = RegexMatchPattern(r'[^\n]*\*/', 'open_block_comment_end')
    # String Quote Characters
    string_quote_characters = MatcherBag(CharMatchPattern("'", 'string_literal'))  # NB in Mysql this should also include "
    # Identifier Quote Characters
    identifier_quote_characters = MatcherBag(CharMatchPattern('"', 'object_literal'))  # NB in Mysql this should be `

    outside_block_comment_matchers = MatcherBag(
        whitespace_regex, inline_comment_regex, closed_block_comment,
        open_block_comment_start, string_quote_characters, identifier_quote_characters)
    
    inside_block_comment_matchers = MatcherBag(open_block_comment_end)


LexerContext = namedtuple('LexerContext', ['dialect', 'multiline_comment_active'])


class RecursiveLexer(object):
    def __init__(self, dialect=AnsiSQLDialiect):
        self.dialect = dialect

    def lex(self, chunk, **start_context):
        # Match based on available matchers
        matches = self.dialect.outside_block_comment_matchers.chunkmatch(chunk)
        # examine first match
        first_match = matches[0]
        if first_match[0].chunk == chunk.chunk:
            # We've matched the whole string!
            cs = ChunkString(chunk.contextualise(first_match[2].name))
            if first_match[2].name == 'open_block_comment_start':
                new_context = {**start_context}
                new_context['block_comment_open'] = True
                return cs, new_context
            else:
                return cs, start_context
        elif first_match[0].start_pos == chunk.start_pos:
            # The match starts at the beginning, but isn't the whole string
            matched_chunk, remainder_chunk = chunk.split_at(len(first_match[0]))
            new_context = {**start_context}
            if first_match[2].name == 'open_block_comment_start':
                new_context['block_comment_open'] = True
            remainder_string, end_context = self.lex(remainder_chunk, **new_context)
            return ChunkString(matched_chunk.contextualise(first_match[2].name)) + remainder_string, end_context
        elif first_match[0].start_pos:
            # The match doesn't start at the beginning, we've got content first
            content_chunk, remainder_chunk = chunk.split_at(first_match[1])
            remainder_string, end_context = self.lex(remainder_chunk, **start_context)
            return ChunkString(content_chunk.contextualise('content')) + remainder_string, end_context
        else:
            # No Match, just content
            return ChunkString(chunk.contextualise('content')), start_context


def parse_file(file_obj, dialect=AnsiSQLDialiect):
    """ Take a file like oject and parse it into chunks """
    # Create some variables to hold context between lines
    string_buffer = None
    chunk_buffer = []
    context = {}
    rl = RecursiveLexer()
    for idx, line in enumerate(file_obj, start=1):
        line_chunk = PositionedChunk(line, 0, idx, None)
        # context carries on
        res, context = rl.lex(line_chunk, **context)
        click.echo(res)


@click.command()
@click.option('--dialect', default='ansi', help='The dialect of SQL to lint')
@click.argument('paths', nargs=-1)
def sqlfluff_lint(dialect, paths):
    """Lint SQL files"""
    click.echo('Linting... [Dialect: {0}]'.format(dialect))
    click.echo(paths)
    if len(paths) == 0:
        # No paths specified - assume local
        paths = ('.',)
    for path in paths:
        click.echo('Linting: {0}'.format(path))
        # Iterate through files recursively in the specified directory (if it's a directory)
        # or read the file directly if it's not
    click.echo("Loading the example file...")
    for fname in ['example.sql', 'example-tab.sql']:
        click.echo(fname)
        with open(fname) as f:
            parse_file(f)


if __name__ == '__main__':
    sqlfluff_lint()
