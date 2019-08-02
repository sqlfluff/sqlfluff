""" The Test file for The New Parser (Marker Classes)"""

import pytest

from sqlfluff.parser_2.grammar import OneOf, Sequence, GreedyUntil, ContainsOnly
from sqlfluff.parser_2.markers import FilePositionMarker
from sqlfluff.parser_2.segments_core import KeywordSegment, StrippedRawCodeSegment, WhitespaceSegment

# NB: All of these tests depend somewhat on the KeywordSegment working as planned


@pytest.fixture(scope="module")
def seg_list():
    return [
        StrippedRawCodeSegment(
            'bar',
            FilePositionMarker.from_fresh()
        ),
        WhitespaceSegment(
            ' \t ',
            FilePositionMarker.from_fresh().advance_by('bar')
        ),
        StrippedRawCodeSegment(
            'foo',
            FilePositionMarker.from_fresh().advance_by('bar \t ')
        ),
        StrippedRawCodeSegment(
            'baar',
            FilePositionMarker.from_fresh().advance_by('bar \t foo')
        ),
        WhitespaceSegment(
            ' \t ',
            FilePositionMarker.from_fresh().advance_by('bar \t foobaar')
        ),
    ]


def test__parser_2__grammar_oneof(seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = OneOf(fs, bs)
    # Matching the list shouldn't work
    assert g.match(seg_list) is None
    # Matching either element should return the relevant one
    assert g.match(seg_list[0]) == bs('bar', seg_list[0].pos_marker)
    assert g.match(seg_list[2]) == fs('foo', seg_list[2].pos_marker)


def test__parser_2__grammar_sequence(seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = Sequence(bs, fs)
    gc = Sequence(bs, fs, code_only=False)
    # Matching the full list shouldn't work
    assert g.match(seg_list) is None
    # Matching a short list shouldn't work (even though the first matches)
    assert g.match([seg_list[0]]) is None
    # Matching a list of the right length shouldn't match if the content isn't the same
    assert g.match(seg_list[1:]) is None
    # Matching a slice should
    assert g.match(seg_list[:3]) == [
        bs('bar', seg_list[0].pos_marker),
        seg_list[1],  # This will be the whitespace segment
        fs('foo', seg_list[2].pos_marker)
    ]
    # Matching the slice, but broadening to more than code shouldn't
    assert gc.match(seg_list[:3]) is None


def test__parser_2__grammar_sequence_nested(seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g = Sequence(Sequence(bs, fs), bas)
    # Matching the start of the list shouldn't work
    assert g.match(seg_list[:2]) is None
    # Matching the whole list should, and the result should be flat
    assert g.match(seg_list) == [
        bs('bar', seg_list[0].pos_marker),
        seg_list[1],  # This will be the whitespace segment
        fs('foo', seg_list[2].pos_marker),
        bas('baar', seg_list[3].pos_marker),
        seg_list[4]  # This will be the whitespace segment
    ]


def test__parser_2__grammar_greedyuntil(seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g0 = GreedyUntil(bs)
    g1 = GreedyUntil(fs)
    g2 = GreedyUntil(bas)
    # Greedy matching until the first item should return none
    assert g0.match(seg_list) is None
    # Greedy matching up to foo should return bar (as a raw!)
    assert g1.match(seg_list) == seg_list[:2]
    # Greedy matching up to baar should return bar, foo  (as a raw!)
    assert g2.match(seg_list) == seg_list[:3]


def test__parser_2__grammar_containsonly(seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g0 = ContainsOnly(bs, bas)
    g1 = ContainsOnly('raw')
    g2 = ContainsOnly(fs, bas, bs)
    # Contains only, without matches for all shouldn't match
    assert g0.match(seg_list) is None
    # Contains only, with just the type should return the list as is
    assert g1.match(seg_list) == seg_list
    # Contains only with matches for all should, as the matched versions
    assert g2.match(seg_list) == [
        bs('bar', seg_list[0].pos_marker),
        fs('foo', seg_list[1].pos_marker),
        bas('baar', seg_list[2].pos_marker)
    ]
