""" The Test file for SQLFluff """

from sqlfluff import RecursiveLexer, PositionedChunk, ChunkString


def test__recursive__basic():
    rl = RecursiveLexer()
    pc = PositionedChunk('SELECT\n', 0, 1)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 2
    assert res[0].chunk == 'SELECT'


def test__recursive__multi_whitespace_a():
    rl = RecursiveLexer()
    pc = PositionedChunk('    SELECT    \n', 0, 1)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 3
    assert res[0].content == 'whitespace'
    assert res[1].chunk == 'SELECT'


def test__recursive__multi_whitespace_b():
    # This test requires recursion
    rl = RecursiveLexer()
    pc = PositionedChunk('    SELECT   foo    \n', 0, 1)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 5
    assert res[0].content == 'whitespace'
    assert res[1].chunk == 'SELECT'
    assert res[3].chunk == 'foo'
    assert res[3].start_pos == 13

