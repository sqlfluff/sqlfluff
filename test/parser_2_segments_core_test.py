""" The Test file for The New Parser (Marker Classes)"""

import pytest

import logging

from sqlfluff.parser_2.markers import FilePositionMarker
from sqlfluff.parser_2.segments_base import RawSegment
from sqlfluff.parser_2.segments_core import KeywordSegment, RawCodeSegment


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


@pytest.mark.parametrize(
    "raw",
    [
        "foobar", " foo ", "foo\nbar", "select * from blah",
        "insert into sch.tbl values (1, 2, 3)"
    ]
)
def test__parser_2__core_rawcode_a(raw):
    """ Test the RawCodeSegment and basic parsing """
    rcs = RawCodeSegment(raw, FilePositionMarker.from_fresh())
    # Parse and test reconstruct
    segs = rcs.parse()
    logging.warning(segs)
    assert ''.join([seg.raw for seg in segs]) == raw
    # Check that if there's a newline, that we get it's own segment
    if '\n' in raw:
        assert any([seg.type == 'newline' for seg in segs])


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
    # Match it against the final element
    assert FooKeyword.match(raw_seg_list[1]) == FooKeyword(
        'foo',
        FilePositionMarker.from_fresh().advance_by('bar')
    )
    # Match it against the final element as a list
    assert FooKeyword.match([raw_seg_list[1]]) == FooKeyword(
        'foo',
        FilePositionMarker.from_fresh().advance_by('bar')
    )
