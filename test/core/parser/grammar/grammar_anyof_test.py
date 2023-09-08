"""Tests for the OneOf, AnyOf & AnySetOf grammars.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import pytest

from sqlfluff.core.parser import (
    KeywordSegment,
    RegexParser,
    StringParser,
    WhitespaceSegment,
)
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import OneOf, Sequence
from sqlfluff.core.parser.grammar.anyof import AnySetOf


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
def test__parser__grammar_oneof(seg_list, allow_gaps):
    """Test the OneOf grammar.

    NB: Should behave the same regardless of code_only.

    """
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = OneOf(fs, bs, allow_gaps=allow_gaps)
    ctx = ParseContext(dialect=None)
    # Check directly
    assert g.match(seg_list, parse_context=ctx).matched_segments == (
        KeywordSegment("bar", seg_list[0].pos_marker),
    )
    # Check with a bit of whitespace
    assert not g.match(seg_list[1:], parse_context=ctx)


def test__parser__grammar_oneof_templated(seg_list):
    """Test the OneOf grammar.

    NB: Should behave the same regardless of code_only.

    """
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = OneOf(fs, bs)
    ctx = ParseContext(dialect=None)
    # This shouldn't match, but it *ALSO* shouldn't raise an exception.
    # https://github.com/sqlfluff/sqlfluff/issues/780
    assert not g.match(seg_list[5:], parse_context=ctx)


def test__parser__grammar_oneof_exclude(seg_list):
    """Test the OneOf grammar exclude option."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = OneOf(bs, exclude=Sequence(bs, fs))
    ctx = ParseContext(dialect=None)
    # Just against the first alone
    assert g.match(seg_list[:1], parse_context=ctx)
    # Now with the bit to exclude included
    assert not g.match(seg_list, parse_context=ctx)


def test__parser__grammar_oneof_take_longest_match(seg_list):
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
    assert fooRegex.match(seg_list[2:], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", seg_list[2].pos_marker),
    )
    assert g.match(seg_list[2:], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", seg_list[2].pos_marker),
        KeywordSegment("baar", seg_list[3].pos_marker),
    )


def test__parser__grammar_oneof_take_first(seg_list):
    """Test that the OneOf grammar takes first match in case they are of same length."""
    fooRegex = RegexParser(r"fo{2}", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)

    # Both segments would match "foo"
    # so we test that order matters
    g1 = OneOf(fooRegex, foo)
    g2 = OneOf(foo, fooRegex)
    ctx = ParseContext(dialect=None)
    assert g1.match(seg_list[2:], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", seg_list[2].pos_marker),
    )
    assert g2.match(seg_list[2:], parse_context=ctx).matched_segments == (
        KeywordSegment("foo", seg_list[2].pos_marker),
    )


def test__parser__grammar_anysetof(generate_test_segments):
    """Test the AnySetOf grammar."""
    token_list = ["bar", "  \t ", "foo", "  \t ", "bar"]
    seg_list = generate_test_segments(token_list)

    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = AnySetOf(fs, bs)
    ctx = ParseContext(dialect=None)
    # Check directly
    assert g.match(seg_list, parse_context=ctx).matched_segments == (
        KeywordSegment("bar", seg_list[0].pos_marker),
        WhitespaceSegment("  \t ", seg_list[1].pos_marker),
        KeywordSegment("foo", seg_list[2].pos_marker),
    )
    # Check with a bit of whitespace
    assert not g.match(seg_list[1:], parse_context=ctx)
