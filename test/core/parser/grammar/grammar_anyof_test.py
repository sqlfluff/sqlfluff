"""Tests for the OneOf, AnyOf & AnySetOf grammars.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import pytest

from sqlfluff.core.parser import (
    KeywordSegment,
    RawSegment,
    RegexParser,
    StringParser,
    WhitespaceSegment,
)
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import OneOf, Sequence
from sqlfluff.core.parser.grammar.anyof import AnySetOf
from sqlfluff.core.parser.match_result import MatchResult2
from sqlfluff.core.parser.segments import BaseSegment, EphemeralSegment


class Example1Segment(RawSegment):
    """A minimal example segment for testing."""

    type = "example1"


class Example2Segment(RawSegment):
    """Another minimal example segment for testing."""

    type = "example2"


def test__parser__grammar__oneof__ephemeral_segment(test_segments):
    """A realistic full test of ephemeral segments."""

    class TestSegment(BaseSegment):
        match_grammar = OneOf(
            StringParser("bar", KeywordSegment), ephemeral_name="foofoo"
        )

    ctx = ParseContext(dialect=None)
    m = TestSegment.match(test_segments[:1], ctx)
    # Make sure we've matched
    assert m
    seg = m.matched_segments[0]
    assert isinstance(seg, TestSegment)
    # Check the content is ephemeral
    assert isinstance(seg.segments[0], EphemeralSegment)
    assert seg.segments[0].ephemeral_name == "foofoo"
    # Expand the segment
    result = seg.parse(ctx)
    assert isinstance(result, tuple)
    res = result[0]
    # Check we still have a test segment
    assert isinstance(res, TestSegment)
    # But that it contains a keyword segment now
    assert isinstance(res.segments[0], KeywordSegment)


def test__parser__grammar__oneof__copy():
    """Test grammar copying."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g1 = OneOf(fs, bs)
    # Check copy
    g2 = g1.copy()
    assert g1 == g2
    assert g1 is not g2
    # Check copy insert (start)
    g3 = g1.copy(insert=[bs], at=0)
    assert g3 == OneOf(bs, fs, bs)
    # Check copy insert (mid)
    g4 = g1.copy(insert=[bs], at=1)
    assert g4 == OneOf(fs, bs, bs)
    # Check copy insert (end)
    g5 = g1.copy(insert=[bs], at=-1)
    assert g5 == OneOf(fs, bs, bs)


@pytest.mark.parametrize("allow_gaps", [True, False])
def test__parser__grammar_oneof(test_segments, allow_gaps):
    """Test the OneOf grammar.

    NOTE: Should behave the same regardless of allow_gaps.
    """
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = OneOf(fs, bs, allow_gaps=allow_gaps)
    ctx = ParseContext(dialect=None)
    # Check directly
    assert g.match(test_segments, parse_context=ctx).matched_segments == (
        KeywordSegment("bar", test_segments[0].pos_marker),
    )
    # Check with a bit of whitespace
    assert not g.match(test_segments[1:], parse_context=ctx)


def test__parser__grammar_oneof_templated(test_segments):
    """Test the OneOf grammar.

    NB: Should behave the same regardless of code_only.

    """
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = OneOf(fs, bs)
    ctx = ParseContext(dialect=None)
    # This shouldn't match, but it *ALSO* shouldn't raise an exception.
    # https://github.com/sqlfluff/sqlfluff/issues/780
    assert not g.match(test_segments[5:], parse_context=ctx)


def test__parser__grammar_oneof_exclude(test_segments):
    """Test the OneOf grammar exclude option."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = OneOf(bs, exclude=Sequence(bs, fs))
    ctx = ParseContext(dialect=None)
    # Just against the first alone
    assert g.match(test_segments[:1], parse_context=ctx)
    # Now with the bit to exclude included
    assert not g.match(test_segments, parse_context=ctx)


def test__parser__grammar_oneof_take_longest_match(test_segments):
    """Test that the OneOf grammar takes the longest match."""
    fooRegex = RegexParser(r"fo{2}", KeywordSegment)
    baar = StringParser("baar", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)
    fooBaar = Sequence(
        foo,
        baar,
    )

    # Even if fooRegex comes first, fooBaar
    # is a longer match and should be taken
    g = OneOf(fooRegex, fooBaar)
    ctx = ParseContext(dialect=None)
    assert fooRegex.match(test_segments[2:], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", test_segments[2].pos_marker),
    )
    assert g.match(test_segments[2:], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", test_segments[2].pos_marker),
        KeywordSegment("baar", test_segments[3].pos_marker),
    )


def test__parser__grammar_oneof_take_first(test_segments):
    """Test that the OneOf grammar takes first match in case they are of same length."""
    fooRegex = RegexParser(r"fo{2}", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)

    # Both segments would match "foo"
    # so we test that order matters
    g1 = OneOf(fooRegex, foo)
    g2 = OneOf(foo, fooRegex)
    ctx = ParseContext(dialect=None)
    assert g1.match(test_segments[2:], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", test_segments[2].pos_marker),
    )
    assert g2.match(test_segments[2:], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", test_segments[2].pos_marker),
    )


def test__parser__grammar_oneof_take_first2(test_segments):
    """Test that the OneOf grammar takes first match in case they are of same length."""
    foo1 = StringParser("foo", Example1Segment)
    foo2 = StringParser("foo", Example2Segment)
    ctx = ParseContext(dialect=None)

    # Both segments would match "foo"
    # so we test that order matters
    g1 = OneOf(foo1, foo2)
    result1 = g1.match2(test_segments, 2, ctx)  # 2 is the index of "foo"
    # in g1, the Example1Segment is first.
    assert result1.matched_class is Example1Segment

    g2 = OneOf(foo2, foo1)
    result2 = g2.match2(test_segments, 2, ctx)  # 2 is the index of "foo"
    # in g2, the Example2Segment is first.
    assert result2.matched_class is Example2Segment


def test__parser__grammar_anysetof(generate_test_segments):
    """Test the AnySetOf grammar."""
    token_list = ["bar", "  \t ", "foo", "  \t ", "bar"]
    segments = generate_test_segments(token_list)

    bar = StringParser("bar", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)
    g = AnySetOf(foo, bar)
    ctx = ParseContext(dialect=None)
    # Check directly
    assert g.match(segments, parse_context=ctx).matched_segments == (
        KeywordSegment("bar", segments[0].pos_marker),
        WhitespaceSegment("  \t ", segments[1].pos_marker),
        KeywordSegment("foo", segments[2].pos_marker),
    )
    # Check with a bit of whitespace
    assert not g.match(segments[1:], parse_context=ctx)


def test__parser__grammar_anysetof2(generate_test_segments):
    """Test the AnySetOf grammar."""
    token_list = ["bar", "  \t ", "foo", "  \t ", "bar"]
    segments = generate_test_segments(token_list)

    bar = StringParser("bar", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)
    g = AnySetOf(foo, bar)
    ctx = ParseContext(dialect=None)

    # Check it doesn't match if the start is whitespace.
    assert not g.match2(segments, 1, ctx)

    # Check structure if we start with a match.
    result = g.match2(segments, 0, ctx)
    assert result == MatchResult2(
        matched_slice=slice(0, 3),
        child_matches=(
            MatchResult2(slice(0, 1), KeywordSegment),
            MatchResult2(slice(2, 3), KeywordSegment),
            # NOTE: The second "bar" isn't included because this
            # is any *set* of and we've already have "bar" once.
        ),
    )
