"""The Test file for The New Parser (Lexing steps)."""

import pytest
import logging

from sqlfluff.core.parser import Lexer, CodeSegment, NewlineSegment
from sqlfluff.core.parser.lexer import (
    StringLexer,
    LexMatch,
    RegexLexer,
)
from sqlfluff.core import SQLLexError, FluffConfig


def assert_matches(instring, matcher, matchstring):
    """Assert that a matcher does or doesn't work on a string.

    The optional `matchstring` argument, which can optionally
    be None, allows to either test positive matching of a
    particular string or negative matching (that it explicitly)
    doesn't match.
    """
    res = matcher.match(instring)
    # Check we've got the right type
    assert isinstance(res, LexMatch)
    if matchstring is None:
        assert res.forward_string == instring
        assert res.elements == []
    else:
        assert res.forward_string == instring[len(matchstring) :]
        assert len(res.elements) == 1
        assert res.elements[0].raw == matchstring


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
        # Test strings
        ("*-+bd/", ["*", "-", "+", "bd", "/"]),
        # Test Negatives and Minus
        ("2+4 -5", ["2", "+", "4", " ", "-", "5"]),
        ("when 'Spec\\'s 23' like", ["when", " ", "'Spec\\'s 23'", " ", "like"]),
        ('when "Spec\\"s 23" like', ["when", " ", '"Spec\\"s 23"', " ", "like"]),
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
def test__parser__lexer_string(raw, res):
    """Test the StringLexer."""
    matcher = StringLexer("dot", ".", CodeSegment)
    assert_matches(raw, matcher, res)


@pytest.mark.parametrize(
    "raw,reg,res",
    [
        ("fsaljk", "f", "f"),
        ("fsaljk", r"f", "f"),
        ("fsaljk", r"[fas]*", "fsa"),
        # Matching whitespace segments
        ("   \t   fsaljk", r"[^\S\r\n]*", "   \t   "),
        # Matching whitespace segments (with a newline)
        ("   \t \n  fsaljk", r"[^\S\r\n]*", "   \t "),
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
    """Test the RegexLexer."""
    matcher = RegexLexer("test", reg, CodeSegment)
    with caplog.at_level(logging.DEBUG):
        assert_matches(raw, matcher, res)


def test__parser__lexer_lex_match(caplog):
    """Test the RepeatedMultiMatcher."""
    matchers = [
        StringLexer("dot", ".", CodeSegment),
        RegexLexer("test", r"#[^#]*#", CodeSegment),
    ]
    with caplog.at_level(logging.DEBUG):
        res = Lexer.lex_match("..#..#..#", matchers)
        assert res.forward_string == "#"  # Should match right up to the final element
        assert len(res.elements) == 5
        assert res.elements[2].raw == "#..#"


def test__parser__lexer_fail():
    """Test the how the lexer fails and reports errors."""
    lex = Lexer(config=FluffConfig())

    _, vs = lex.lex("Select \u0394")

    assert len(vs) == 1
    err = vs[0]
    assert isinstance(err, SQLLexError)
    assert err.line_pos == 8


def test__parser__lexer_fail_via_parse():
    """Test the how the parser fails and reports errors while lexing."""
    lexer = Lexer(config=FluffConfig())
    _, vs = lexer.lex("Select \u0394")
    assert vs
    assert len(vs) == 1
    err = vs[0]
    assert isinstance(err, SQLLexError)
    assert err.line_pos == 8


def test__parser__lexer_trim_post_subdivide(caplog):
    """Test a RegexLexer with a trim_post_subdivide function."""
    matcher = [
        RegexLexer(
            "function_script_terminator",
            r";\s+(?!\*)\/(?!\*)|\s+(?!\*)\/(?!\*)",
            CodeSegment,
            segment_kwargs={"type": "function_script_terminator"},
            subdivider=StringLexer(
                "semicolon", ";", CodeSegment, segment_kwargs={"type": "semicolon"}
            ),
            trim_post_subdivide=RegexLexer(
                "newline",
                r"(\n|\r\n)+",
                NewlineSegment,
            ),
        )
    ]
    with caplog.at_level(logging.DEBUG):
        res = Lexer.lex_match(";\n/\n", matcher)
        assert res.elements[0].raw == ";"
        assert res.elements[1].raw == "\n"
        assert res.elements[2].raw == "/"
        assert len(res.elements) == 3
