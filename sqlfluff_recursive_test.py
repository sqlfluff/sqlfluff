""" The Test file for SQLFluff """

import pytest
from sqlfluff import CharMatchPattern, RegexMatchPattern, MatcherBag, RecursiveLexer, PositionedChunk, ChunkString

# ############## Chunks
def test__chunk__split():
    c = PositionedChunk('foobarbar', 10, 20, None)
    a, b = c.split_at(3)
    assert a == PositionedChunk('foo', 10, 20, None)
    assert b == PositionedChunk('barbar', 13, 20, None)


def test__chunk__split_context_error():
    c = PositionedChunk('foobarbar', 10, 20, 'context')
    with pytest.raises(RuntimeError):
        c.split_at(4)


def test__chunk__subchunk():
    c = PositionedChunk('foobarbar', 10, 20, None)
    r = c.subchunk(3,6)
    assert r == PositionedChunk('bar', 13, 20, None)


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


def test__charmatch__chunkmatch():
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


def test__regexmatch__span():
    cmp = RegexMatchPattern(r'"[a-z]+"', None)
    s = 'aefal "fuinef" uynl*fa'
    assert cmp.span(s) == (6, 14)


# ############## Matcher Bag
def test__matcherbag__unique():
    # raise an error that are duplicate names
    with pytest.raises(AssertionError):
        MatcherBag(CharMatchPattern('"', 'foo'), CharMatchPattern('"', 'foo'))


def test__matcherbag__add_unique():
    # raise an error that are duplicate names
    with pytest.raises(AssertionError):
        m = MatcherBag(CharMatchPattern('"', 'foo')) + MatcherBag(CharMatchPattern('"', 'foo'))


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


# ############## LEXER TESTS
def test__recursive__basic():
    rl = RecursiveLexer()
    pc = PositionedChunk('SELECT\n', 0, 1, None)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 2
    assert res[0].chunk == 'SELECT'


def test__recursive__multi_whitespace_a():
    rl = RecursiveLexer()
    pc = PositionedChunk('    SELECT    \n', 0, 1, None)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 3
    assert res[0].context == 'whitespace'
    assert res[1].chunk == 'SELECT'


def test__recursive__multi_whitespace_b():
    # This test requires recursion
    rl = RecursiveLexer()
    pc = PositionedChunk('    SELECT   foo    \n', 0, 1, None)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 5
    assert res[0].context == 'whitespace'
    assert res[1].chunk == 'SELECT'
    assert res[3].chunk == 'foo'
    assert res[3].start_pos == 13


# short term disabled test
def atest__recursive__comment_a():
    # This test requires recursion
    rl = RecursiveLexer()
    # The whitespace on the end of a comment should be it's own chunk
    pc = PositionedChunk('SELECT    -- Testing Comment\n', 0, 1, None)
    res, context = rl.lex(pc)
    assert res.content_list() == ['content', 'whitespace', 'comment', 'whitespace']
    assert res[3].content == '\n'
