"""Tests for any other grammars.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import logging

import pytest

from sqlfluff.core.parser import KeywordSegment, StringParser, SymbolSegment
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import (
    Anything,
    Delimited,
    GreedyUntil,
    Nothing,
    StartsWith,
)
from sqlfluff.core.parser.grammar.noncode import NonCodeMatcher


def test__parser__grammar_startswith_a():
    """Test the StartsWith grammar fails when no terminator supplied."""
    Keyword = StringParser("foo", KeywordSegment)
    with pytest.raises(AssertionError):
        StartsWith(Keyword)


@pytest.mark.parametrize(
    "include_terminator,match_length",
    [
        # NOTE: this case shouldn't include the whitespace between "bar" and "foo".
        (False, 1),
        # ...and in this case it _should_.
        (True, 3),
    ],
)
def test__parser__grammar_startswith_b(
    include_terminator, match_length, seg_list, fresh_ansi_dialect, caplog
):
    """Test the StartsWith grammar with a terminator (included & excluded)."""
    foo = StringParser("foo", KeywordSegment)
    bar = StringParser("bar", KeywordSegment)
    grammar = StartsWith(bar, terminators=[foo], include_terminator=include_terminator)
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        m = grammar.match(seg_list, parse_context=ctx)
        assert len(m) == match_length


@pytest.mark.parametrize(
    "token_list,min_delimiters,allow_gaps,allow_trailing,match_len",
    [
        # Basic testing
        (["bar", " \t ", ".", "    ", "bar"], None, True, False, 5),
        (["bar", " \t ", ".", "    ", "bar", "    "], None, True, False, 6),
        # Testing allow_trailing
        (["bar", " \t ", ".", "   "], None, True, False, 0),
        (["bar", " \t ", ".", "   "], None, True, True, 4),
        # Testing the implications of allow_gaps
        (["bar", " \t ", ".", "    ", "bar"], 0, True, False, 5),
        (["bar", " \t ", ".", "    ", "bar"], 0, False, False, 1),
        (["bar", " \t ", ".", "    ", "bar"], 1, True, False, 5),
        (["bar", " \t ", ".", "    ", "bar"], 1, False, False, 0),
        (["bar", ".", "bar"], None, True, False, 3),
        (["bar", ".", "bar"], None, False, False, 3),
        (["bar", ".", "bar"], 1, True, False, 3),
        (["bar", ".", "bar"], 1, False, False, 3),
        # Check we still succeed with something trailing right on the end.
        (["bar", ".", "bar", "foo"], 1, False, False, 3),
        # Check min_delimiters. There's a delimiter here, but not enough to match.
        (["bar", ".", "bar", "foo"], 2, True, False, 0),
    ],
)
def test__parser__grammar_delimited(
    min_delimiters,
    allow_gaps,
    allow_trailing,
    token_list,
    match_len,
    caplog,
    generate_test_segments,
    fresh_ansi_dialect,
):
    """Test the Delimited grammar when not code_only."""
    seg_list = generate_test_segments(token_list)
    g = Delimited(
        StringParser("bar", KeywordSegment),
        delimiter=StringParser(".", SymbolSegment),
        allow_gaps=allow_gaps,
        allow_trailing=allow_trailing,
        min_delimiters=min_delimiters,
    )
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Matching with whitespace shouldn't match if we need at least one delimiter
        m = g.match(seg_list, parse_context=ctx)
        assert len(m) == match_len


@pytest.mark.parametrize(
    "keyword,slice_len",
    [
        # Basic testing
        ("foo", 1),
        # Greedy matching until the first item should return none
        ("bar", 0),
        # NOTE: the greedy until "baar" won't match because baar is
        # a keyword and therefore is required to have whitespace
        # before it. In the test sequence "baar" does not.
        # See `greedy_match()` for details.
        ("baar", 6),
    ],
)
def test__parser__grammar_greedyuntil(keyword, seg_list, slice_len, fresh_ansi_dialect):
    """Test the GreedyUntil grammar."""
    grammar = GreedyUntil(StringParser(keyword, KeywordSegment))
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    assert (
        grammar.match(seg_list, parse_context=ctx).matched_segments
        == seg_list[:slice_len]
    )


def test__parser__grammar_greedyuntil_bracketed(bracket_seg_list, fresh_ansi_dialect):
    """Test the GreedyUntil grammar with brackets."""
    fs = StringParser("foo", KeywordSegment)
    g = GreedyUntil(fs)
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    # Check that we can make it past the brackets
    match = g.match(bracket_seg_list, parse_context=ctx)
    assert len(match) == 4
    # Check we successfully constructed a bracketed segment
    assert match.matched_segments[2].is_type("bracketed")
    assert match.matched_segments[2].raw == "(foo    )"
    # Check that the unmatched segments is foo AND the whitespace
    assert len(match.unmatched_segments) == 2


def test__parser__grammar_anything(seg_list, fresh_ansi_dialect):
    """Test the Anything grammar."""
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    assert Anything().match(seg_list, parse_context=ctx)


def test__parser__grammar_nothing(seg_list, fresh_ansi_dialect):
    """Test the Nothing grammar."""
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    assert not Nothing().match(seg_list, parse_context=ctx)


def test__parser__grammar_noncode(seg_list, fresh_ansi_dialect):
    """Test the NonCodeMatcher."""
    ctx = ParseContext(dialect=fresh_ansi_dialect)
    m = NonCodeMatcher().match(seg_list[1:], parse_context=ctx)
    # NonCode Matcher doesn't work with simple
    assert NonCodeMatcher().simple(ctx) is None
    # We should match one and only one segment
    assert len(m) == 1
