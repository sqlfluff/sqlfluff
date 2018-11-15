""" Contains SQL Dialects """

from .matchers import RegexMatchPattern, CharMatchPattern, SingleCharMatchPattern, MatcherBag


def dialect_selector(s):
    lookup = {
        'ansi': AnsiSQLDialiect
    }
    return lookup[s]


class AnsiSQLDialiect(object):
    name = 'ansi'
    # Whitespace is what divides other bits of syntax
    whitespace_regex = RegexMatchPattern(r'\s+', 'whitespace')
    # Anything after an inline comment gets chunked together as not code
    # Priority required here, because it's potentially ambiguous with the operator regex
    inline_comment_regex = RegexMatchPattern(r'(--|#)[^\n]*', 'comment', priority=2)  # In MySQL, we need a space after the '--'
    # Anything between the first and last part of this tuple counts as not code
    # Priority required because of divide operator or multiply operator
    closed_block_comment = RegexMatchPattern(r'/\*[^\n]*\*/', 'closed_block_comment', priority=2)
    open_block_comment_start = RegexMatchPattern(r'/\*[^\n]', 'open_block_comment_start', priority=2)
    open_block_comment_end = RegexMatchPattern(r'[^\n]*\*/', 'open_block_comment_end', priority=2)
    # String Quote Characters
    string_quote_characters = MatcherBag(CharMatchPattern("'", 'string_literal'))  # NB in Mysql this should also include "
    # Identifier Quote Characters
    identifier_quote_characters = MatcherBag(CharMatchPattern('"', 'object_literal'))  # NB in Mysql this should be `
    # Singleton Match Patterns
    comma_characters = SingleCharMatchPattern(',', 'comma')

    # NB: A Star and a mulitply look the same to a lexer!!!! We'll have to
    # resolve that ambiguity later, for now it's a multiply
    # star_characters = SingleCharMatchPattern('*', 'star')

    # Operator Match Patterns (A slightly larger supserset of ansi)
    operator_regex = RegexMatchPattern(r'(\+|-|\*|/)', 'operator')
    # These are case insensitive but require spaces to distinguish from words
    text_operator_regex = RegexMatchPattern(r'(?i)(or|and)', 'operator')

    # Bracket matchers
    open_bracket_matcher = SingleCharMatchPattern('(', 'open_bracket')
    close_bracket_matcher = SingleCharMatchPattern(')', 'close_bracket')

    outside_block_comment_matchers = MatcherBag(
        whitespace_regex, inline_comment_regex, closed_block_comment,
        open_block_comment_start, string_quote_characters, identifier_quote_characters,
        comma_characters, operator_regex, open_bracket_matcher, close_bracket_matcher)

    inside_block_comment_matchers = MatcherBag(open_block_comment_end)
