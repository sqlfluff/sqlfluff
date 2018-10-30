""" The Test file for SQLFluff """

from sqlfluff import RecursiveLexer, PositionedChunk, ChunkString


def test__recursive__basic():
    rl = RecursiveLexer()
    pc = PositionedChunk('SELECT\n', 0, 1)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 2
    assert res[0].chunk == 'SELECT'


def test__recursive__multi_whitespace():
    rl = RecursiveLexer()
    pc = PositionedChunk('    SELECT    \n', 0, 1)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 3
    assert res[0].content == 'whitespace'
    assert res[1].chunk == 'SELECT'


