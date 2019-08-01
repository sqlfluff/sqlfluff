""" The Test file for The New Parser (Marker Classes)"""

import pytest

from sqlfluff.parser_2.grammar import OneOf, Sequence, GreedyUntil
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


def test__parser_2__grammar_sequence_nested(raw_seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g = Sequence(Sequence(bs, fs), bas)
    # Matching the start of the list shouldn't work
    assert g.match(raw_seg_list[:2]) is None
    # Matching the whole list should, and the result should be flat
    assert g.match(raw_seg_list) == [
        bs('bar', raw_seg_list[0].pos_marker),
        fs('foo', raw_seg_list[1].pos_marker),
        bas('baar', raw_seg_list[2].pos_marker)
    ]


def test__parser_2__grammar_greedyuntil(raw_seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g0 = GreedyUntil(bs)
    g1 = GreedyUntil(fs)
    g2 = GreedyUntil(bas)
    # Greedy matching until the first item should return none
    assert g0.match(raw_seg_list) is None
    # Greedy matching up to foo should return bar (as a raw!)
    assert g1.match(raw_seg_list) == raw_seg_list[:1]
    # Greedy matching up to baar should return bar, foo  (as a raw!)
    assert g2.match(raw_seg_list) == raw_seg_list[:2]
