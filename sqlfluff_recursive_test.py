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


def test__recursive__comment_a():
    # This test requires recursion
    rl = RecursiveLexer()
    # The whitespace on the end of a comment should be it's own chunk
    pc = PositionedChunk('SELECT    -- Testing Comment\n', 0, 1)
    res, context = rl.lex(pc)
    assert res.content_list() == ['content', 'whitespace', 'comment', 'whitespace']
    assert res[3].content == '\n'
