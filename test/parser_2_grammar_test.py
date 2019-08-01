""" The Test file for The New Parser (Marker Classes)"""

import pytest

from sqlfluff.parser_2.grammar import OneOf, Sequence
from sqlfluff.parser_2.markers import FilePositionMarker
from sqlfluff.parser_2.segments_base import RawSegment
from sqlfluff.parser_2.segments_core import KeywordSegment

# NB: All of these tests depend somewhat on the KeywordSegment working as planned


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
            'baar',
            FilePositionMarker.from_fresh().advance_by('barfoo')
        )
    ]


def test__parser_2__grammar_oneof(raw_seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = OneOf(fs, bs)
    # Matching the list shouldn't work
    assert g.match(raw_seg_list) is None
    # Matching either element should return the relevant one
    assert g.match(raw_seg_list[0]) == bs('bar', raw_seg_list[0].pos_marker)
    assert g.match(raw_seg_list[1]) == fs('foo', raw_seg_list[1].pos_marker)


def test__parser_2__grammar_sequence(raw_seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = Sequence(bs, fs)
    # Matching the full list shouldn't work
    assert g.match(raw_seg_list) is None
    # Matching a short list shouldn't work (even though the first matches)
    assert g.match([raw_seg_list[0]]) is None
    # Matching a list of the right length shouldn't match if the content isn't the same
    assert g.match(raw_seg_list[1:]) is None
    # Matching a slice should
    assert g.match(raw_seg_list[:2]) == [
        bs('bar', raw_seg_list[0].pos_marker),
        fs('foo', raw_seg_list[1].pos_marker)
    ]
