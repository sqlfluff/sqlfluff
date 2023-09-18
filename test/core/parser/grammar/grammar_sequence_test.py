"""Tests for the Sequence grammar.

NOTE: All of these tests depend somewhat on the KeywordSegment working as planned.
"""

import logging
from os import getenv

import pytest

from sqlfluff.core.parser import Indent, KeywordSegment, StringParser, WhitespaceSegment
from sqlfluff.core.parser.context import ParseContext
from sqlfluff.core.parser.grammar import Conditional, Sequence
from sqlfluff.core.parser.types import ParseMode


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


def test__parser__grammar_sequence_repr():
    """Test the Sequence grammar __repr__ method."""
    bar = StringParser("bar", KeywordSegment)
    assert repr(bar) == "<StringParser: 'BAR'>"
    foo = StringParser("foo", KeywordSegment)
    sequence = Sequence(bar, foo)
    assert (
        repr(sequence) == "<Sequence: [<StringParser: 'BAR'>, <StringParser: 'FOO'>]>"
    )


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


@pytest.mark.parametrize(
    "mode,sequence,terminators,input_slice,output_tuple",
    [
        # #####
        # Test matches where we should get something, and that's
        # the whole sequence.
        # NOTE: Include a little whitespace in the slice (i.e. the first _two_
        # segments) to check that it isn't included in the match.
        (ParseMode.STRICT, ["a"], [], slice(None, 2), (("keyword", "a"),)),
        (ParseMode.GREEDY, ["a"], [], slice(None, 2), (("keyword", "a"),)),
        (ParseMode.GREEDY_ONCE_STARTED, ["a"], [], slice(None, 2), (("keyword", "a"),)),
        # #####
        # Test matching on sequences where we run out of segments before matching
        # the whole sequence.
        # STRICT returns no match.
        (ParseMode.STRICT, ["a", "b"], [], slice(None, 2), ()),
        # GREEDY & GREEDY_ONCE_STARTED returns the content as unparsable, and
        # still don't include the trailing whitespace. The return value does
        # however have the matched "a" as a keyword and not a raw.
        (
            ParseMode.GREEDY,
            ["a", "b"],
            [],
            slice(None, 2),
            (("unparsable", (("keyword", "a"),)),),
        ),
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a", "b"],
            [],
            slice(None, 2),
            (("unparsable", (("keyword", "a"),)),),
        ),
        # #####
        # Test matching on sequences where we fail to match the first element.
        # STRICT & GREEDY_ONCE_STARTED return no match.
        (ParseMode.STRICT, ["b"], [], slice(None, 2), ()),
        (ParseMode.GREEDY_ONCE_STARTED, ["b"], [], slice(None, 2), ()),
        # GREEDY claims the remaining elements (unmutated) as unparsable, but
        # does not claim any trailing whitespace.
        (
            ParseMode.GREEDY,
            ["b"],
            [],
            slice(None, 2),
            (("unparsable", (("raw", "a"),)),),
        ),
        # #####
        # Test matches where we should match the sequence fully, but there's more
        # to match.
        # First without terminators...
        # STRICT ignores the rest.
        (ParseMode.STRICT, ["a"], [], slice(None, 5), (("keyword", "a"),)),
        # The GREEDY modes claim the rest as unparsable.
        # NOTE: the whitespace in between is _not_ unparsable.
        (
            ParseMode.GREEDY,
            ["a"],
            [],
            slice(None, 5),
            (
                ("keyword", "a"),
                ("whitespace", " "),
                ("unparsable", (("raw", "b"), ("whitespace", " "), ("raw", "c"))),
            ),
        ),
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a"],
            [],
            slice(None, 5),
            (
                ("keyword", "a"),
                ("whitespace", " "),
                ("unparsable", (("raw", "b"), ("whitespace", " "), ("raw", "c"))),
            ),
        ),
        # Second *with* terminators.
        # NOTE: The whitespace before the terminator is not included.
        (ParseMode.STRICT, ["a"], ["c"], slice(None, 5), (("keyword", "a"),)),
        (
            ParseMode.GREEDY,
            ["a"],
            ["c"],
            slice(None, 5),
            (("keyword", "a"), ("whitespace", " "), ("unparsable", (("raw", "b"),))),
        ),
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a"],
            ["c"],
            slice(None, 5),
            (("keyword", "a"), ("whitespace", " "), ("unparsable", (("raw", "b"),))),
        ),
        # #####
        # Test matches where we match the first element of a sequence but not the
        # second (with terminators)
        (ParseMode.STRICT, ["a", "x"], ["c"], slice(None, 5), ()),
        # NOTE: For GREEDY modes, the matched portion is not included as an "unparsable"
        # only the portion which failed to match. The terminator is not included and
        # the matched portion is still mutated correctly.
        (
            ParseMode.GREEDY,
            ["a", "x"],
            ["c"],
            slice(None, 5),
            (("keyword", "a"), ("whitespace", " "), ("unparsable", (("raw", "b"),))),
        ),
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a", "x"],
            ["c"],
            slice(None, 5),
            (("keyword", "a"), ("whitespace", " "), ("unparsable", (("raw", "b"),))),
        ),
        # #####
        # Test competition between sequence elements and terminators.
        # In GREEDY_ONCE_STARTED, the first element is matched before any terminators.
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a"],
            ["a"],
            slice(None, 2),
            (("keyword", "a"),),
        ),
        # In GREEDY, the terminator is matched first and so takes precedence.
        (
            ParseMode.GREEDY,
            ["a"],
            ["a"],
            slice(None, 2),
            (),
        ),
        # NOTE: In these last two cases, the "b" isn't included because it acted as
        # a terminator before being considered in the sequence.
        (
            ParseMode.GREEDY_ONCE_STARTED,
            ["a", "b"],
            ["b"],
            slice(None, 3),
            (("unparsable", (("keyword", "a"),)),),
        ),
        (
            ParseMode.GREEDY,
            ["a", "b"],
            ["b"],
            slice(None, 3),
            (("unparsable", (("keyword", "a"),)),),
        ),
    ],
)
def test__parser__grammar_sequence_modes(
    mode,
    sequence,
    terminators,
    input_slice,
    output_tuple,
    generate_test_segments,
    fresh_ansi_dialect,
):
    """Test the Sequence grammar with various parse modes.

    In particular here we're testing the treatment of unparsable
    sections.
    """
    segments = generate_test_segments(["a", " ", "b", " ", "c", "d", " ", "d"])
    # Dialect is required here only to have access to bracket segments.
    ctx = ParseContext(dialect=fresh_ansi_dialect)

    _seq = Sequence(
        *(StringParser(e, KeywordSegment) for e in sequence),
        parse_mode=mode,
        terminators=[StringParser(e, KeywordSegment) for e in terminators]
    )
    _match = _seq.match(segments[input_slice], ctx)
    # If we're expecting an output tuple, assert the match is truthy.
    if output_tuple:
        assert _match
    _result = tuple(
        e.to_tuple(show_raw=True, code_only=False) for e in _match.matched_segments
    )
    assert _result == output_tuple
