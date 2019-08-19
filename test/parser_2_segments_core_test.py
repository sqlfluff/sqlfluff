""" The Test file for The New Parser (Marker Classes)"""

import pytest


from sqlfluff.parser_2.markers import FilePositionMarker
from sqlfluff.parser_2.segments_base import RawSegment
from sqlfluff.parser_2.segments_core import KeywordSegment


@pytest.fixture(scope="module")
def raw_seg_list():
    return [
        RawSegment(
            'bar',
            FilePositionMarker.from_fresh()
        ),
        RawSegment(
            'foo',
            FilePositionMarker.from_fresh().advance_by('bar')
        )
    ]


def test__parser_2__core_keyword(raw_seg_list):
    """ Test the Mystical KeywordSegment """
    # First make a keyword
    FooKeyword = KeywordSegment.make('foo')
    # Check it looks as expected
    assert issubclass(FooKeyword, KeywordSegment)
    assert FooKeyword.__name__ == "FOO_KeywordSegment"
    assert FooKeyword._template == 'FOO'
    # Match it against a list and check it doesn't match
    assert FooKeyword.match(raw_seg_list) is None
    # Match it against a the first element and check it doesn't match
    assert FooKeyword.match(raw_seg_list[0]) is None
    # Match it against a the first element as a list and check it doesn't match
    assert FooKeyword.match([raw_seg_list[0]]) is None
    # Match it against the final element (returns tuple)
    assert FooKeyword.match(raw_seg_list[1]) == (FooKeyword(
        'foo',
        FilePositionMarker.from_fresh().advance_by('bar')
    ),)
    # Match it against the final element as a list (returns tuple)
    assert FooKeyword.match([raw_seg_list[1]]) == (FooKeyword(
        'foo',
        FilePositionMarker.from_fresh().advance_by('bar')
    ),)
