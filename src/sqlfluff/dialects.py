""" Contains SQL Dialects """

from .matchers import RegexMatchPattern, CharMatchPattern, SingleCharMatchPattern, MatcherBag


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
    # Singleton Match Patterns
    comma_characters = SingleCharMatchPattern(',', 'comma')
    star_characters = SingleCharMatchPattern('*', 'star')

    outside_block_comment_matchers = MatcherBag(
        whitespace_regex, inline_comment_regex, closed_block_comment,
        open_block_comment_start, string_quote_characters, identifier_quote_characters,
        comma_characters, star_characters)

    inside_block_comment_matchers = MatcherBag(open_block_comment_end)
