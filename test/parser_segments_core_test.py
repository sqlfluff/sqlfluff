""" The Test file for The New Parser (Marker Classes)"""

import pytest


from sqlfluff.parser.markers import FilePositionMarker
from sqlfluff.parser.segments_base import RawSegment
from sqlfluff.parser.segments_common import KeywordSegment


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
        ),
        RawSegment(
            'bar',
            FilePositionMarker.from_fresh().advance_by('barfoo')
        )
    ]


def test__parser__core_keyword(raw_seg_list):
    """ Test the Mystical KeywordSegment """
    # First make a keyword
    FooKeyword = KeywordSegment.make('foo')
    # Check it looks as expected
    assert issubclass(FooKeyword, KeywordSegment)
    assert FooKeyword.__name__ == "FOO_KeywordSegment"
    assert FooKeyword._template == 'FOO'
    # Match it against a list and check it doesn't match
    assert not FooKeyword.match(raw_seg_list)
    # Match it against a the first element and check it doesn't match
    assert not FooKeyword.match(raw_seg_list[0])
    # Match it against a the first element as a list and check it doesn't match
    assert not FooKeyword.match([raw_seg_list[0]])
    # Match it against the final element (returns tuple)
    m = FooKeyword.match(raw_seg_list[1])
    assert m
    assert m.matched_segments[0].raw == 'foo'
    assert isinstance(m.matched_segments[0], FooKeyword)
    # Match it against the final element as a list
    assert FooKeyword.match([raw_seg_list[1]])
    # Match it against a list slice and check it still works
    assert FooKeyword.match(raw_seg_list[1:])
