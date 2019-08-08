""" The Test file for The New Parser (Marker Classes)"""

import pytest
import logging

from sqlfluff.parser_2.lexer import Lexer
from sqlfluff.parser_2.lexer import SingletonMatcher, LexMatch
from sqlfluff.parser_2.segments_base import RawSegment
from sqlfluff.parser_2.markers import FilePositionMarker


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
        # ("b.c", ['a', '.', 'b']),
        # ("abc \n \t def  ;blah", ['abc', ' ', '\n', ' \t ', 'def', '  ', ';', 'blah'])
    ]
)
def test__parser_2__lexer_obj(raw, res, caplog):
    lex = Lexer()
    with caplog.at_level(logging.DEBUG):
        assert lex.lex(raw) == res


def test__parser_2__lexer_singleton():
    matcher = SingletonMatcher(
        "dot", ".", RawSegment.make('.', name='dot', is_code=True)
    )
    assert_matches('.fsaljk', matcher, '.')
    assert_matches('fsaljk', matcher, None)
