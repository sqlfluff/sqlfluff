"""Tests for the Sequence grammar.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import logging
from os import getenv

from sqlfluff.core.parser import Indent, KeywordSegment, StringParser, WhitespaceSegment
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Conditional, Sequence


def test__parser__grammar_sequence(seg_list, caplog):
    """Test the Sequence grammar."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = Sequence(bs, fs)
    # If running in the test environment, assert that Sequence recognises this
    if getenv("SQLFLUFF_TESTENV", ""):
        assert g.test_env
    gc = Sequence(bs, fs, allow_gaps=False)
    ctx = ParseContext(dialect=None)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Should be able to match the list using the normal matcher
        logging.info("#### TEST 1")
        m = g.match(seg_list, parse_context=ctx)
        assert m
        assert len(m) == 3
        assert m.matched_segments == (
            KeywordSegment("bar", seg_list[0].pos_marker),
            seg_list[1],  # This will be the whitespace segment
            KeywordSegment("foo", seg_list[2].pos_marker),
        )
        # Shouldn't with the allow_gaps matcher
        logging.info("#### TEST 2")
        assert not gc.match(seg_list, parse_context=ctx)
        # Shouldn't match even on the normal one if we don't start at the beginning
        logging.info("#### TEST 2")
        assert not g.match(seg_list[1:], parse_context=ctx)


def test__parser__grammar_sequence_repr():
    """Test the Sequence grammar __repr__ method."""
    bar = StringParser("bar", KeywordSegment)
    assert repr(bar) == "<StringParser: 'BAR'>"
    foo = StringParser("foo", KeywordSegment)
    sequence = Sequence(bar, foo)
    assert (
        repr(sequence) == "<Sequence: [<StringParser: 'BAR'>, <StringParser: 'FOO'>]>"
    )


def test__parser__grammar_sequence_nested(seg_list, caplog):
    """Test the Sequence grammar when nested."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    bas = StringParser("baar", KeywordSegment)
    g = Sequence(Sequence(bs, fs), bas)
    ctx = ParseContext(dialect=None)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Matching the start of the list shouldn't work
        logging.info("#### TEST 1")
        assert not g.match(seg_list[:2], parse_context=ctx)
        # Matching the whole list should, and the result should be flat
        logging.info("#### TEST 2")
        assert g.match(seg_list, parse_context=ctx).matched_segments == (
            KeywordSegment("bar", seg_list[0].pos_marker),
            seg_list[1],  # This will be the whitespace segment
            KeywordSegment("foo", seg_list[2].pos_marker),
            KeywordSegment("baar", seg_list[3].pos_marker)
            # NB: No whitespace at the end, this shouldn't be consumed.
        )


def test__parser__grammar_sequence_indent(seg_list, caplog):
    """Test the Sequence grammar with indents."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = Sequence(Indent, bs, fs)
    ctx = ParseContext(dialect=None)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        m = g.match(seg_list, parse_context=ctx)
        assert m
        # check we get an indent.
        assert isinstance(m.matched_segments[0], Indent)
        assert isinstance(m.matched_segments[1], KeywordSegment)


def test__parser__grammar_sequence_indent_conditional(seg_list, caplog):
    """Test the Sequence grammar with indents."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    # We will assume the default config has indented_joins = False.
    # We're testing without explicitly setting the `config_type` because
    # that's the assumed way of using the grammar in practice.
    g = Sequence(
        Conditional(Indent, indented_joins=False),
        bs,
        Conditional(Indent, indented_joins=True),
        fs,
    )
    ctx = ParseContext(dialect=None)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        m = g.match(seg_list, parse_context=ctx)
        assert m
        # Check we get an Indent.
        assert isinstance(m.matched_segments[0], Indent)
        assert isinstance(m.matched_segments[1], KeywordSegment)
        # check the whitespace is still there
        assert isinstance(m.matched_segments[2], WhitespaceSegment)
        # Check the second Indent does not appear
        assert not isinstance(m.matched_segments[3], Indent)
        assert isinstance(m.matched_segments[3], KeywordSegment)
