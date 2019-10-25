""" The Test file for The New Parser (Marker Classes)"""

import pytest
import logging

from sqlfluff.parser.lexer import Lexer
from sqlfluff.parser.lexer import SingletonMatcher, LexMatch, RegexMatcher, RepeatedMultiMatcher
from sqlfluff.parser.segments_base import RawSegment
from sqlfluff.parser.markers import FilePositionMarker


def assert_matches(instring, matcher, matchstring):
    start_pos = FilePositionMarker.from_fresh()
    res = matcher.match(instring, start_pos)
    # Check we've got the right type
    assert isinstance(res, LexMatch)
    if matchstring is None:
        assert res.new_string == instring
        assert res.new_pos == start_pos
        assert res.segments == tuple()
    else:
        new_pos = start_pos.advance_by(matchstring)
        assert res.new_string == instring[len(matchstring):]
        assert res.new_pos == new_pos
        assert len(res.segments) == 1
        assert res.segments[0].raw == matchstring


@pytest.mark.parametrize(
    "raw,res",
    [
        ("a b", ['a', ' ', 'b']),
        ("b.c", ['b', '.', 'c']),
        ("abc \n \t def  ;blah", ['abc', ' ', '\n', ' \t ', 'def', '  ', ';', 'blah']),
        # Test Quotes
        ("abc'\n \"\t' \"de`f\"", ['abc', "'\n \"\t'", ' ', '"de`f"']),
        # Test Comments
        ("abc -- comment \nblah", ['abc', ' ', "-- comment ", "\n", "blah"]),
        ("abc # comment \nblah", ['abc', ' ', "# comment ", "\n", "blah"]),
        ("abc /* comment \nblah*/", ['abc', ' ', "/* comment \nblah*/"]),
        # Test Singletons
        ("*-+bd/", ['*', '-', '+', 'bd', '/'])
    ]
)
def test__parser__lexer_obj(raw, res, caplog):
    lex = Lexer()
    with caplog.at_level(logging.DEBUG):
        assert [seg.raw for seg in lex.lex(raw)] == res


@pytest.mark.parametrize(
    "raw,res",
    [
        (".fsaljk", '.'),
        ("fsaljk", None),
    ]
)
def test__parser__lexer_singleton(raw, res):
    matcher = SingletonMatcher(
        "dot", ".", RawSegment.make('.', name='dot', is_code=True)
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
        ("' something exciting \t\n '   \t \n  fsaljk", r"'[^']*'", "' something exciting \t\n '"),
    ]
)
def test__parser__lexer_regex(raw, reg, res, caplog):
    matcher = RegexMatcher(
        "test", reg, RawSegment.make('test', name='test')
    )
    with caplog.at_level(logging.DEBUG):
        assert_matches(raw, matcher, res)


def test__parser__lexer_multimatcher(caplog):
    matcher = RepeatedMultiMatcher(
        SingletonMatcher(
            "dot", ".", RawSegment.make('.', name='dot', is_code=True)
        ),
        RegexMatcher(
            "test", r"#[^#]*#", RawSegment.make('test', name='test')
        )
    )
    start_pos = FilePositionMarker.from_fresh()
    with caplog.at_level(logging.DEBUG):
        res = matcher.match('..#..#..#', start_pos)
        assert res.new_string == '#'  # Should match right up to the final element
        assert res.new_pos == start_pos.advance_by('..#..#..')
        assert len(res.segments) == 5
        assert res.segments[2].raw == '#..#'
