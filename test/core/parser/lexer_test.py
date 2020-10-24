"""The Test file for The New Parser (Lexing steps)."""

import pytest
import logging

from sqlfluff.core.parser import Lexer
from sqlfluff.core.parser.lexer import (
    SingletonMatcher,
    LexMatch,
    RegexMatcher,
    RepeatedMultiMatcher,
)
from sqlfluff.core.parser import RawSegment, FileSegment, FilePositionMarker
from sqlfluff.core import SQLLexError, FluffConfig


def assert_matches(instring, matcher, matchstring):
    """Assert that a matcher does or doesn't work on a string.

    The optional `matchstring` argument, which can optionally
    be None, allows to either test positive matching of a
    particular string or negative matching (that it explicitly)
    doesn't match.
    """
    start_pos = FilePositionMarker.from_fresh()
    res = matcher.match(instring, start_pos)
    # Check we've got the right type
    assert isinstance(res, LexMatch)
    if matchstring is None:
        assert res.new_string == instring
        assert res.new_pos == start_pos
        assert res.segments == ()  # tuple
    else:
        new_pos = start_pos.advance_by(matchstring)
        assert res.new_string == instring[len(matchstring) :]
        assert res.new_pos == new_pos
        assert len(res.segments) == 1
        assert res.segments[0].raw == matchstring


@pytest.mark.parametrize(
    "raw,res",
    [
        ("a b", ["a", " ", "b"]),
        ("b.c", ["b", ".", "c"]),
        ("abc \n \t def  ;blah", ["abc", " ", "\n", " \t ", "def", "  ", ";", "blah"]),
        # Test Quotes
        ('abc\'\n "\t\' "de`f"', ["abc", "'\n \"\t'", " ", '"de`f"']),
        # Test Comments
        ("abc -- comment \nblah", ["abc", " ", "-- comment ", "\n", "blah"]),
        ("abc # comment \nblah", ["abc", " ", "# comment ", "\n", "blah"]),
        # Note the more complicated parsing of block comments.
        # This tests subdivision and trimming (incl the empty case)
        ("abc /* comment \nblah*/", ["abc", " ", "/* comment", " ", "\n", "blah*/"]),
        ("abc /*\n\t\n*/", ["abc", " ", "/*", "\n", "\t", "\n", "*/"]),
        # Test Singletons
        ("*-+bd/", ["*", "-", "+", "bd", "/"]),
        # Test Negatives and Minus
        ("2+4 -5", ["2", "+", "4", " ", "-", "5"]),
    ],
)
def test__parser__lexer_obj(raw, res, caplog):
    """Test the lexer splits as expected in a selection of cases."""
    lex = Lexer(config=FluffConfig())
    with caplog.at_level(logging.DEBUG):
        lexing_segments, _ = lex.lex(raw)
        assert [seg.raw for seg in lexing_segments] == res


@pytest.mark.parametrize(
    "raw,res",
    [
        (".fsaljk", "."),
        ("fsaljk", None),
    ],
)
def test__parser__lexer_singleton(raw, res):
    """Test the SingletonMatcher."""
    matcher = SingletonMatcher(
        "dot", ".", RawSegment.make(".", name="dot", is_code=True)
    )
    assert_matches(raw, matcher, res)


@pytest.mark.parametrize(
    "raw,reg,res",
    [
        ("fsaljk", "f", "f"),
        ("fsaljk", r"f", "f"),
        ("fsaljk", r"[fas]*", "fsa"),
        # Matching whitespace segments
        ("   \t   fsaljk", r"[\t ]*", "   \t   "),
        # Matching whitespace segments (with a newline)
        ("   \t \n  fsaljk", r"[\t ]*", "   \t "),
        # Matching quotes containing stuff
        ("'something boring'   \t \n  fsaljk", r"'[^']*'", "'something boring'"),
        (
            "' something exciting \t\n '   \t \n  fsaljk",
            r"'[^']*'",
            "' something exciting \t\n '",
        ),
    ],
)
def test__parser__lexer_regex(raw, reg, res, caplog):
    """Test the RegexMatcher."""
    matcher = RegexMatcher("test", reg, RawSegment.make("test", name="test"))
    with caplog.at_level(logging.DEBUG):
        assert_matches(raw, matcher, res)


def test__parser__lexer_multimatcher(caplog):
    """Test the RepeatedMultiMatcher."""
    matcher = RepeatedMultiMatcher(
        SingletonMatcher("dot", ".", RawSegment.make(".", name="dot", is_code=True)),
        RegexMatcher("test", r"#[^#]*#", RawSegment.make("test", name="test")),
    )
    start_pos = FilePositionMarker.from_fresh()
    with caplog.at_level(logging.DEBUG):
        res = matcher.match("..#..#..#", start_pos)
        assert res.new_string == "#"  # Should match right up to the final element
        assert res.new_pos == start_pos.advance_by("..#..#..")
        assert len(res.segments) == 5
        assert res.segments[2].raw == "#..#"


def test__parser__lexer_fail():
    """Test the how the lexer fails and reports errors."""
    lex = Lexer(config=FluffConfig())

    _, vs = lex.lex("Select \u0394")

    assert len(vs) == 1
    err = vs[0]
    assert isinstance(err, SQLLexError)
    assert err.pos_marker().char_pos == 7


def test__parser__lexer_fail_via_parse():
    """Test the how the parser fails and reports errors while lexing."""
    _, vs = FileSegment.from_raw("Select \u0394", config=FluffConfig())
    assert vs
    assert len(vs) == 1
    err = vs[0]
    assert isinstance(err, SQLLexError)
    assert err.pos_marker().char_pos == 7
