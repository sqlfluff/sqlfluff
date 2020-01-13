"""The Test file for The New Parser (Grammar Classes)."""

import pytest
import logging

from sqlfluff.parser.grammar import (OneOf, Sequence, GreedyUntil, ContainsOnly,
                                     Delimited, BaseGrammar, StartsWith)
from sqlfluff.parser.segments_base import ParseContext
from sqlfluff.parser.segments_common import KeywordSegment
from sqlfluff.dialects import ansi_dialect

# NB: All of these tests depend somewhat on the KeywordSegment working as planned


@pytest.fixture(scope="function")
def seg_list(generate_test_segments):
    """A preset list of segments for testing."""
    return generate_test_segments(['bar', ' \t ', 'foo', 'baar', ' \t '])


@pytest.fixture(scope="function")
def bracket_seg_list(generate_test_segments):
    """Another preset list of segments for testing."""
    return generate_test_segments([
        'bar', ' \t ', '(', 'foo', '    ', ')', 'baar', ' \t ', 'foo'
    ])


def test__parser__grammar__base__code_only_sensitive_match(seg_list):
    """Test the _code_only_sensitive_match method of the BaseGrammar."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    c = ParseContext()
    # Matching the first element of the list
    m = BaseGrammar._code_only_sensitive_match(seg_list, bs, c, code_only=False)
    assert m.matched_segments == (bs('bar', seg_list[0].pos_marker),)
    # Matching with a bit of whitespace before
    m = BaseGrammar._code_only_sensitive_match(seg_list[1:], fs, c, code_only=True)
    assert m.matched_segments == (seg_list[1], fs('foo', seg_list[2].pos_marker))
    # Matching with a bit of whitespace before (not code_only)
    m = BaseGrammar._code_only_sensitive_match(seg_list[1:], fs, c, code_only=False)
    assert not m
    # Matching with whitespace after
    m = BaseGrammar._code_only_sensitive_match(seg_list[:2], bs, c, code_only=True)
    assert m.matched_segments == (bs('bar', seg_list[0].pos_marker), seg_list[1])


def test__parser__grammar__base__look_ahead_match(seg_list):
    """Test the _look_ahead_match method of the BaseGrammar."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    c = ParseContext()

    # Basic version, we should find bar first
    m = BaseGrammar._look_ahead_match(seg_list, [fs, bs], c)
    assert isinstance(m, tuple)
    assert len(m) == 3
    assert m[0] == ()
    assert m[2] == bs
    # NB the middle element is a match object
    assert m[1].matched_segments == (bs('bar', seg_list[0].pos_marker),)

    # Look ahead for foo
    m = BaseGrammar._look_ahead_match(seg_list, [fs], c, code_only=False)
    assert m[1].matched_segments == (fs('foo', seg_list[2].pos_marker),)

    # Allow leading whitespace
    m = BaseGrammar._look_ahead_match(seg_list, [fs], c, code_only=True)
    assert m[1].matched_segments == (seg_list[1], fs('foo', seg_list[2].pos_marker))


def test__parser__grammar__base__bracket_sensitive_look_ahead_match(bracket_seg_list):
    """Test the _bracket_sensitive_look_ahead_match method of the BaseGrammar."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    # We need a dialect here to do bracket matching
    c = ParseContext(dialect=ansi_dialect)

    # Basic version, we should find bar first
    m = BaseGrammar._bracket_sensitive_look_ahead_match(bracket_seg_list, [fs, bs], c)
    assert isinstance(m, tuple)
    assert len(m) == 3
    assert m[0] == ()
    assert m[2] == bs
    # NB the middle element is a match object
    assert m[1].matched_segments == (bs('bar', bracket_seg_list[0].pos_marker),)

    # Look ahead for foo, we should find the one AFTER the brackets, not the
    # on IN the brackets.
    m = BaseGrammar._bracket_sensitive_look_ahead_match(bracket_seg_list, [fs], c)
    assert isinstance(m, tuple)
    assert len(m) == 3
    assert len(m[0]) == 7  # NB: The bracket segments will have been mutated, so we can't directly compare
    assert m[2] == fs
    # We'll end up matching the whitespace with the keyword
    assert m[1].matched_segments == (bracket_seg_list[7], fs('foo', bracket_seg_list[8].pos_marker))


def test__parser__grammar_oneof(seg_list):
    """Test the OneOf grammar."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = OneOf(fs, bs, code_only=False)
    c = ParseContext()
    # Check directly
    assert g.match(seg_list, parse_context=c).matched_segments == (bs('bar', seg_list[0].pos_marker),)
    # Check with a bit of whitespace
    m = g.match(seg_list[1:], parse_context=c)
    assert not m


def test__parser__grammar_oneof_codeonly(seg_list, caplog):
    """Test the OneOf grammar when using the code_only option."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = OneOf(fs, bs)
    c = ParseContext()
    with caplog.at_level(logging.DEBUG):
        # Check directly
        assert g.match(seg_list, parse_context=c).matched_segments == (bs('bar', seg_list[0].pos_marker), seg_list[1])
        # Check with a bit of whitespace
        m = g.match(seg_list[1:], parse_context=c)
        assert m
        assert m.matched_segments[1] == fs('foo', seg_list[2].pos_marker)


def test__parser__grammar_startswith_a(seg_list, caplog):
    """Test the StartsWith grammar simply."""
    baar = KeywordSegment.make('baar')
    bar = KeywordSegment.make('bar')
    c = ParseContext(dialect=ansi_dialect)
    with caplog.at_level(logging.DEBUG):
        assert StartsWith(bar).match(seg_list, parse_context=c)
    with caplog.at_level(logging.DEBUG):
        assert not StartsWith(baar).match(seg_list, parse_context=c)


def test__parser__grammar_startswith_b(seg_list, caplog):
    """Test the StartsWith grammar with a terminator (included & exluded)."""
    baar = KeywordSegment.make('baar')
    bar = KeywordSegment.make('bar')
    c = ParseContext(dialect=ansi_dialect)
    with caplog.at_level(logging.DEBUG):
        m = StartsWith(bar, terminator=baar).match(seg_list, parse_context=c)
        assert len(m) == 3
    with caplog.at_level(logging.DEBUG):
        m = StartsWith(bar, terminator=baar, include_terminator=True).match(seg_list, parse_context=c)
        # NB: We'll end up matching the terminating whitespace too
        assert len(m) == 5


def test__parser__grammar_sequence(seg_list, caplog):
    """Test the Sequence grammar."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = Sequence(bs, fs)
    gc = Sequence(bs, fs, code_only=False)
    c = ParseContext()
    with caplog.at_level(logging.DEBUG):
        # Should be able to match the list using the normal matcher
        logging.info("#### TEST 1")
        m = g.match(seg_list, parse_context=c)
        assert m
        assert len(m) == 3
        assert m.matched_segments == (
            bs('bar', seg_list[0].pos_marker),
            seg_list[1],  # This will be the whitespace segment
            fs('foo', seg_list[2].pos_marker)
        )
        # Shouldn't with the code_only matcher
        logging.info("#### TEST 2")
        assert not gc.match(seg_list, parse_context=c)
        # Shouldn't match even on the normal one if we don't start at the beginning
        logging.info("#### TEST 2")
        assert not g.match(seg_list[1:], parse_context=c)


def test__parser__grammar_sequence_nested(seg_list, caplog):
    """Test the Sequence grammar when nested."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g = Sequence(Sequence(bs, fs), bas)
    c = ParseContext()
    with caplog.at_level(logging.DEBUG):
        # Matching the start of the list shouldn't work
        logging.info("#### TEST 1")
        assert not g.match(seg_list[:2], parse_context=c)
        # Matching the whole list should, and the result should be flat
        logging.info("#### TEST 2")
        assert g.match(seg_list, parse_context=c).matched_segments == (
            bs('bar', seg_list[0].pos_marker),
            seg_list[1],  # This will be the whitespace segment
            fs('foo', seg_list[2].pos_marker),
            bas('baar', seg_list[3].pos_marker),
            seg_list[4]  # This will be the whitespace segment
        )


def test__parser__grammar_delimited(caplog, generate_test_segments):
    """Test the Delimited grammar."""
    seg_list = generate_test_segments(['bar', ' \t ', ',', '    ', 'bar', '    '])
    bs = KeywordSegment.make('bar')
    comma = KeywordSegment.make(',', name='comma')
    expectation = (
        bs('bar', seg_list[0].pos_marker),
        seg_list[1],  # This will be the whitespace segment
        comma(',', seg_list[2].pos_marker),
        seg_list[3],  # This will be the whitespace segment
        bs('bar', seg_list[4].pos_marker),
        seg_list[5]  # This will be the whitespace segment
    )
    g = Delimited(bs, delimiter=comma)
    gt = Delimited(bs, delimiter=comma, allow_trailing=True)
    c = ParseContext(dialect=ansi_dialect)
    with caplog.at_level(logging.DEBUG):
        # Matching not quite the full list shouldn't work
        logging.info("#### TEST 1")
        assert not g.match(seg_list[:4], parse_context=c)
        # Matching not quite the full list should work if we allow trailing
        logging.info("#### TEST 1")
        assert gt.match(seg_list[:4], parse_context=c)
        # Matching up to 'bar' should
        logging.info("#### TEST 3")
        assert g._match(seg_list[:5], parse_context=c).matched_segments == expectation[:5]
        # Matching the full list ALSO should, because it's just whitespace
        logging.info("#### TEST 4")
        assert g.match(seg_list, parse_context=c).matched_segments == expectation[:6]
        # We should have matched the trailing whitespace in this case.


def test__parser__grammar_delimited_not_code_only(caplog, generate_test_segments):
    """Test the Delimited grammar when not code_only."""
    seg_list_a = generate_test_segments(['bar', ' \t ', '.', '    ', 'bar'])
    seg_list_b = generate_test_segments(['bar', '.', 'bar'])
    bs = KeywordSegment.make('bar')
    dot = KeywordSegment.make('.', name='dot')
    g = Delimited(bs, delimiter=dot, code_only=False)
    c = ParseContext(dialect=ansi_dialect)
    with caplog.at_level(logging.DEBUG):
        # Matching with whitespace shouldn't match
        # TODO: dots should be parsed out EARLY
        logging.info("#### TEST 1")
        assert not g.match(seg_list_a, parse_context=c)
        # Matching up to 'bar' should
        logging.info("#### TEST 2")
        assert g.match(seg_list_b, parse_context=c) is not None


def test__parser__grammar_greedyuntil(seg_list):
    """Test the GreedyUntil grammar."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g0 = GreedyUntil(bs)
    g1 = GreedyUntil(fs, code_only=False)
    g2 = GreedyUntil(bas)
    c = ParseContext(dialect=ansi_dialect)
    # Greedy matching until the first item should return none
    assert not g0.match(seg_list, parse_context=c)
    # Greedy matching up to foo should return bar (as a raw!)
    assert g1.match(seg_list, parse_context=c).matched_segments == seg_list[:2]
    # Greedy matching up to baar should return bar, foo  (as a raw!)
    assert g2.match(seg_list, parse_context=c).matched_segments == seg_list[:3]


def test__parser__grammar_greedyuntil_bracketed(bracket_seg_list):
    """Test the GreedyUntil grammar with brackets."""
    fs = KeywordSegment.make('foo')
    g = GreedyUntil(fs, code_only=False)
    c = ParseContext(dialect=ansi_dialect)
    # Check that we can make it past the brackets
    assert len(g.match(bracket_seg_list, parse_context=c)) == 8


def test__parser__grammar_containsonly(seg_list):
    """Test the ContainsOnly grammar."""
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g0 = ContainsOnly(bs, bas)
    g1 = ContainsOnly('raw')
    g2 = ContainsOnly(fs, bas, bs)
    g3 = ContainsOnly(fs, bas, bs, code_only=False)
    c = ParseContext()
    # Contains only, without matches for all shouldn't match
    assert not g0.match(seg_list, parse_context=c)
    # Contains only, with just the type should return the list as is
    assert g1.match(seg_list, parse_context=c) == seg_list
    # Contains only with matches for all should, as the matched versions
    assert g2.match(seg_list, parse_context=c).matched_segments == (
        bs('bar', seg_list[0].pos_marker),
        seg_list[1],  # This will be the whitespace segment
        fs('foo', seg_list[2].pos_marker),
        bas('baar', seg_list[3].pos_marker),
        seg_list[4]  # This will be the whitespace segment
    )
    # When we consider mode than code then it shouldn't work
    assert not g3.match(seg_list, parse_context=c)
