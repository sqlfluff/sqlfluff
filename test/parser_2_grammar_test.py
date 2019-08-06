""" The Test file for The New Parser (Marker Classes)"""

import pytest
import logging

from sqlfluff.parser_2.grammar import (OneOf, Sequence, GreedyUntil, ContainsOnly,
                                       Delimited)
from sqlfluff.parser_2.markers import FilePositionMarker
from sqlfluff.parser_2.segments_core import (KeywordSegment, StrippedRawCodeSegment, WhitespaceSegment,
                                             QuotedSegment, NewlineSegment, CommentSegment)

# NB: All of these tests depend somewhat on the KeywordSegment working as planned


def generate_test_segments(elems):
    """ This function isn't totally robust, but good enough
    for testing. Use with caution. """
    buff = []
    raw_buff = ''
    for elem in elems:
        if set(elem) <= set([' ', '\t']):
            cls = WhitespaceSegment
        elif set(elem) <= set(['\n']):
            cls = NewlineSegment
        elif elem.startswith('--'):
            cls = CommentSegment
        elif elem.startswith('"') or elem.startswith("'"):
            cls = QuotedSegment
        else:
            cls = StrippedRawCodeSegment

        buff.append(
            cls(
                elem,
                FilePositionMarker.from_fresh().advance_by(raw_buff)
            )
        )
        raw_buff += elem
    return buff


@pytest.fixture(scope="module")
def seg_list():
    return generate_test_segments(['bar', ' \t ', 'foo', 'baar', ' \t '])


def test__parser_2__grammar_oneof(seg_list):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = OneOf(fs, bs)
    # Matching the list shouldn't work
    assert g.match(seg_list) is None
    # Matching either element should return the relevant one
    assert g.match(seg_list[0]) == bs('bar', seg_list[0].pos_marker)
    assert g.match(seg_list[2]) == fs('foo', seg_list[2].pos_marker)


def test__parser_2__grammar_sequence(seg_list, caplog):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    g = Sequence(bs, fs)
    gc = Sequence(bs, fs, code_only=False)
    with caplog.at_level(logging.DEBUG):
        # Matching the full list shouldn't work
        logging.info("#### TEST 1")
        assert g.match(seg_list) is None
        # Matching a short list shouldn't work (even though the first matches)
        logging.info("#### TEST 2")
        assert g.match([seg_list[0]]) is None
        # Matching a list of the right length shouldn't match if the content isn't the same
        logging.info("#### TEST 3")
        assert g.match(seg_list[1:]) is None
        # Matching a slice should
        logging.info("#### TEST 4")
        assert g.match(seg_list[:3]) == [
            bs('bar', seg_list[0].pos_marker),
            seg_list[1],  # This will be the whitespace segment
            fs('foo', seg_list[2].pos_marker)
        ]
        # Matching the slice, but broadening to more than code shouldn't
        logging.info("#### TEST 5")
        assert gc.match(seg_list[:3]) is None


def test__parser_2__grammar_sequence_nested(seg_list, caplog):
    fs = KeywordSegment.make('foo')
    bs = KeywordSegment.make('bar')
    bas = KeywordSegment.make('baar')
    g = Sequence(Sequence(bs, fs), bas)
    with caplog.at_level(logging.DEBUG):
        # Matching the start of the list shouldn't work
        logging.info("#### TEST 1")
        assert g.match(seg_list[:2]) is None
        # Matching the whole list should, and the result should be flat
        logging.info("#### TEST 2")
        assert g.match(seg_list) == [
            bs('bar', seg_list[0].pos_marker),
            seg_list[1],  # This will be the whitespace segment
            fs('foo', seg_list[2].pos_marker),
            bas('baar', seg_list[3].pos_marker),
            seg_list[4]  # This will be the whitespace segment
        ]


def test__parser_2__grammar_delimited(caplog):
    seg_list = generate_test_segments(['bar', ' \t ', ',', '    ', 'bar', '    '])
    bs = KeywordSegment.make('bar')
    comma = KeywordSegment.make(',', name='comma')
    expectation = [
        bs('bar', seg_list[0].pos_marker),
        seg_list[1],  # This will be the whitespace segment
        comma(',', seg_list[2].pos_marker),
        seg_list[3],  # This will be the whitespace segment
        bs('bar', seg_list[4].pos_marker),
        seg_list[5]  # This will be the whitespace segment
    ]
    g = Delimited(bs, delimiter=comma)
    with caplog.at_level(logging.DEBUG):
        # Matching not quite the full list shouldn't work
        logging.info("#### TEST 1")
        assert g.match(seg_list[:4]) is None
        # Matching up to 'bar' should
        logging.info("#### TEST 2")
        assert g.match(seg_list[:5]) == expectation[:5]
        # Matching the full list ALSO should, because it's just whitespace
        logging.info("#### TEST 3")
        assert g.match(seg_list) == expectation


def test__parser_2__grammar_delimited_not_code_only(caplog):
    seg_list_a = generate_test_segments(['bar', ' \t ', '.', '    ', 'bar'])
    seg_list_b = generate_test_segments(['bar', '.', 'bar'])
    bs = KeywordSegment.make('bar')
    dot = KeywordSegment.make('.', name='dot')
    g = Delimited(bs, delimiter=dot, code_only=False)
    with caplog.at_level(logging.DEBUG):
        # Matching with whitespace shouldn't match
        # TODO: dots should be parsed out EARLY
        logging.info("#### TEST 1")
        assert g.match(seg_list_a) is None
        # Matching up to 'bar' should
        logging.info("#### TEST 2")
        assert g.match(seg_list_b) is not None


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
    g1 = ContainsOnly('strippedcode')
    g2 = ContainsOnly(fs, bas, bs)
    g3 = ContainsOnly(fs, bas, bs, code_only=False)
    # Contains only, without matches for all shouldn't match
    assert g0.match(seg_list) is None
    # Contains only, with just the type should return the list as is
    assert g1.match(seg_list) == seg_list
    # Contains only with matches for all should, as the matched versions
    assert g2.match(seg_list) == [
        bs('bar', seg_list[0].pos_marker),
        seg_list[1],  # This will be the whitespace segment
        fs('foo', seg_list[2].pos_marker),
        bas('baar', seg_list[3].pos_marker),
        seg_list[4]  # This will be the whitespace segment
    ]
    # When we consider mode than code then it shouldn't work
    assert g3.match(seg_list) is None
