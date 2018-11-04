""" The Test file for Chunks """

import pytest

from sqlfluff.matchers import CharMatchPattern, SingleCharMatchPattern, RegexMatchPattern, MatcherBag
from sqlfluff.chunks import PositionedChunk


# ############## Matchers
def test__charmatch__basic_1():
    cmp = CharMatchPattern('s', None)
    s = 'aefalfuinsefuynlsfa'
    assert cmp.first_match_pos(s) == 9


def test__charmatch__none():
    cmp = CharMatchPattern('s', None)
    s = 'aefalfuin^efuynl*fa'
    assert cmp.first_match_pos(s) is None


def test__charmatch__span():
    cmp = CharMatchPattern('"', None)
    s = 'aefal "fuin^ef" uynl*fa'
    assert cmp.span(s) == (6, 15)


def test__charmatch__chunkmatch_1():
    cmp = CharMatchPattern('"', None)
    chk = PositionedChunk('aefal "fuin^ef" uynl*fa', 13, 20, None)
    sub_chunk = cmp.chunkmatch(chk)
    assert sub_chunk is not None
    assert sub_chunk == PositionedChunk('"fuin^ef"', 13 + 6, 20, 'match')


def test__charmatch__chunkmatch_2():
    cmp = CharMatchPattern('a', 'foo')
    chk = PositionedChunk('asdfbjkebkjaekljds', 13, 20, None)
    sub_chunk = cmp.chunkmatch(chk)
    assert sub_chunk == PositionedChunk('asdfbjkebkja', 13, 20, 'match')


def test__charmatch__chunkmatch_3():
    # Check for an no match scenario
    cmp = CharMatchPattern('a', None)
    chk = PositionedChunk('sdflkg;j;d;sflkgjds', 13, 20, None)
    sub_chunk = cmp.chunkmatch(chk)
    assert sub_chunk is None


def test__regexmatch__span():
    cmp = RegexMatchPattern(r'"[a-z]+"', None)
    s = 'aefal "fuinef" uynl*fa'
    assert cmp.span(s) == (6, 14)


def test__singlecharmatch__none():
    cmp = SingleCharMatchPattern('*', None)
    chk = PositionedChunk('aefal "fuin^ef" uynlfa', 13, 20, None)
    sub_chunk = cmp.chunkmatch(chk)
    assert sub_chunk is None


def test__singlecharmatch__chunkmatch_1():
    cmp = SingleCharMatchPattern('*', None)
    # Check that it only matches once!
    chk = PositionedChunk('aefal "fuin^ef" uynl*fa**', 13, 20, None)
    sub_chunk = cmp.chunkmatch(chk)
    assert sub_chunk is not None
    assert sub_chunk == PositionedChunk('*', 13 + 20, 20, 'match')


# ############## Matcher Bag
def test__matcherbag__unique():
    # raise an error that are duplicate names
    with pytest.raises(AssertionError):
        MatcherBag(CharMatchPattern('"', 'foo'), CharMatchPattern('"', 'foo'))


def test__matcherbag__add_unique():
    # raise an error that are duplicate names
    with pytest.raises(AssertionError):
        MatcherBag(CharMatchPattern('"', 'foo')) + MatcherBag(CharMatchPattern('"', 'foo'))


def test__matcherbag__add_bag():
    # check we can make a bag out of another bag
    bag = MatcherBag(CharMatchPattern('a', 'foo'), MatcherBag(CharMatchPattern('b', 'bar')))
    bag2 = MatcherBag(bag, CharMatchPattern('c', 'bim'))
    assert len(bag2) == 3


def test__matcherbag__chunkmatch_a():
    a = CharMatchPattern('a', 'foo')
    b = CharMatchPattern('b', 'bar')
    m = MatcherBag(a, b)
    chk = PositionedChunk('asdfbjkebkjaekljds', 13, 20, None)
    matches = m.chunkmatch(chk)
    assert len(matches) == 2
    assert matches == [
        (PositionedChunk('asdfbjkebkja', 13, 20, 'match'), 0, a),
        (PositionedChunk('bjkeb', 13 + 4, 20, 'match'), 4, b)]


def test__matcherbag__chunkmatch_b():
    """ A more complicated matcher test, explicitly testing sorting """
    k = CharMatchPattern('k', 'bim')
    b = CharMatchPattern('b', 'bar')
    a = CharMatchPattern('a', 'foo')
    r = RegexMatchPattern(r'e[a-z][a-df-z]+e[a-z]', 'eee')
    m = MatcherBag(k, b, a, r)
    chk = PositionedChunk('asdfbjkebkjaekljds', 11, 2, None)
    matches = m.chunkmatch(chk)
    assert matches == [
        (PositionedChunk('asdfbjkebkja', 11, 2, 'match'), 0, a),
        (PositionedChunk('bjkeb', 11 + 4, 2, 'match'), 4, b),
        (PositionedChunk('kebk', 11 + 6, 2, 'match'), 6, k),
        (PositionedChunk('ebkjaek', 11 + 7, 2, 'match'), 7, r)]
