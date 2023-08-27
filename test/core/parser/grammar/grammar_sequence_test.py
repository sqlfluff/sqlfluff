"""Tests for the Sequence grammar.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import logging
from os import getenv

from sqlfluff.core.parser import (
    KeywordSegment,
    StringParser,
    WhitespaceSegment,
    Indent,
    Dedent,
)
from sqlfluff.core.parser.match_result import MatchResult2
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Sequence, Conditional


def test__parser__grammar_sequence(test_segments, caplog):
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
        m = g.match(test_segments, parse_context=ctx)
        assert m
        assert len(m) == 3
        assert m.matched_segments == (
            KeywordSegment("bar", test_segments[0].pos_marker),
            test_segments[1],  # This will be the whitespace segment
            KeywordSegment("foo", test_segments[2].pos_marker),
        )
        # Shouldn't with the allow_gaps matcher
        logging.info("#### TEST 2")
        assert not gc.match(test_segments, parse_context=ctx)
        # Shouldn't match even on the normal one if we don't start at the beginning
        logging.info("#### TEST 2")
        assert not g.match(test_segments[1:], parse_context=ctx)


def test__parser__grammar_sequence_nested(test_segments, caplog):
    """Test the Sequence grammar when nested."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    bas = StringParser("baar", KeywordSegment)
    g = Sequence(Sequence(bs, fs), bas)
    ctx = ParseContext(dialect=None)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Matching the start of the list shouldn't work
        logging.info("#### TEST 1")
        assert not g.match(test_segments[:2], parse_context=ctx)
        # Matching the whole list should, and the result should be flat
        logging.info("#### TEST 2")
        assert g.match(test_segments, parse_context=ctx).matched_segments == (
            KeywordSegment("bar", test_segments[0].pos_marker),
            test_segments[1],  # This will be the whitespace segment
            KeywordSegment("foo", test_segments[2].pos_marker),
            KeywordSegment("baar", test_segments[3].pos_marker)
            # NB: No whitespace at the end, this shouldn't be consumed.
        )


def test__parser__grammar_sequence_nested_match2(test_segments, caplog):
    """Test the Sequence grammar when nested."""
    bar = StringParser("bar", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)
    baar = StringParser("baar", KeywordSegment)
    g = Sequence(Sequence(bar, foo), baar)

    ctx = ParseContext(dialect=None)
    # Confirm the structure of the test segments:
    assert [s.raw for s in test_segments] == ["bar", " \t ", "foo", "baar", " \t ", ""]
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Matching just the start of the list shouldn't work.
        result1 = g.match2(test_segments[:3], 0, ctx)

    assert not result1  # Check it returns falsy
    assert result1 == MatchResult2(
        matched_slice=slice(0, 3),  # NOTE: One of these is space.
        child_matches=(
            # NOTE: Two child matches, both clean. These
            # *were* in the initial list and should still have
            # matched.
            # It's also important that the subsequence has been flattened
            # here. There isn't a sub-match for the inner sequence. That's
            # because it didn't have a class attached to it.
            MatchResult2(
                matched_slice=slice(0, 1),
                matched_class=KeywordSegment,
            ),
            MatchResult2(
                matched_slice=slice(2, 3),
                matched_class=KeywordSegment,
            ),
        ),
        # ...but the overall match is partial and unclean.
        is_clean=False,
    )

    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        # Matching the whole list should.
        result2 = g.match2(test_segments, 0, ctx)

    assert result2  # Check it returns truthy
    assert result2 == MatchResult2(
        matched_slice=slice(0, 4),  # NOTE: One of these is space.
        child_matches=(
            MatchResult2(
                matched_slice=slice(0, 1),
                matched_class=KeywordSegment,
            ),
            MatchResult2(
                matched_slice=slice(2, 3),
                matched_class=KeywordSegment,
            ),
            MatchResult2(
                matched_slice=slice(3, 4),
                matched_class=KeywordSegment,
            ),
        ),
    )


def test__parser__grammar_sequence_indent(test_segments, caplog):
    """Test the Sequence grammar with indents."""
    bs = StringParser("bar", KeywordSegment)
    fs = StringParser("foo", KeywordSegment)
    g = Sequence(Indent, bs, fs)
    ctx = ParseContext(dialect=None)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        m = g.match(test_segments, parse_context=ctx)
        assert m
        # check we get an indent.
        assert isinstance(m.matched_segments[0], Indent)
        assert isinstance(m.matched_segments[1], KeywordSegment)


def test__parser__grammar_sequence_indent_conditional(test_segments, caplog):
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
        m = g.match(test_segments, parse_context=ctx)
        assert m
        # Check we get an Indent.
        assert isinstance(m.matched_segments[0], Indent)
        assert isinstance(m.matched_segments[1], KeywordSegment)
        # check the whitespace is still there
        assert isinstance(m.matched_segments[2], WhitespaceSegment)
        # Check the second Indent does not appear
        assert not isinstance(m.matched_segments[3], Indent)
        assert isinstance(m.matched_segments[3], KeywordSegment)


def test__parser__grammar_sequence_indent_conditional_match2(test_segments, caplog):
    """Test the Sequence grammar with indents."""
    bar = StringParser("bar", KeywordSegment)
    foo = StringParser("foo", KeywordSegment)
    # We will assume the default config has indented_joins = False.
    # We're testing without explicitly setting the `config_type` because
    # that's the assumed way of using the grammar in practice.
    g = Sequence(
        Dedent,
        Conditional(Indent, indented_joins=False),
        bar,
        Conditional(Indent, indented_joins=True),
        foo,
        Dedent,
    )
    ctx = ParseContext(dialect=None)
    with caplog.at_level(logging.DEBUG, logger="sqlfluff.parser"):
        m = g.match2(test_segments, 0, parse_context=ctx)

    assert m == MatchResult2(
        matched_slice=slice(0, 3),  # NOTE: One of these is space.
        child_matches=(
            # The two child keywords
            MatchResult2(
                matched_slice=slice(0, 1),
                matched_class=KeywordSegment,
            ),
            MatchResult2(
                matched_slice=slice(2, 3),
                matched_class=KeywordSegment,
            ),
        ),
        insert_segments=(
            (0, Dedent),  # The starting, unconditional dedent.
            (0, Indent),  # The conditional (activated) Indent.
            # NOTE: There *isn't* the other Indent.
            (3, Dedent),  # The closing unconditional dedent.
            # NOTE: This last one is still included even though it's
            # after the last matched segment.
        ),
    )
