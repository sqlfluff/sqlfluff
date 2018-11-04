""" The Test file for SQLFluff """

import io

from sqlfluff.chunks import PositionedChunk, ChunkString
from sqlfluff.lexer import RecursiveLexer


# ############## LEXER TESTS
def test__recursive__basic_1():
    rl = RecursiveLexer()
    pc = PositionedChunk('   ', 0, 1, None)
    res, context = rl.lex(pc)
    assert isinstance(res, ChunkString)
    assert len(res) == 1
    assert res[0].chunk == '   '


def test__recursive__basic_2():
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


def test__recursive__comment_a():
    # This test requires recursion
    rl = RecursiveLexer()
    # The whitespace on the end of a comment should be it's own chunk
    pc = PositionedChunk('SELECT    -- Testing Comment\n', 0, 1, None)
    res, context = rl.lex(pc)
    assert res.context_list() == ['content', 'whitespace', 'comment', 'whitespace']
    assert res[3].chunk == '\n'


def test__recursive__lex_chunk_buffer():
    # This test requires recursion
    rl = RecursiveLexer()
    # The whitespace on the end of a comment should be it's own chunk
    pc_list = [PositionedChunk('SELECT\n', 0, 1, None), PositionedChunk('NOTHING\n', 0, 2, None)]
    res, context = rl.lex_chunk_buffer(pc_list)
    assert res.context_list() == ['content', 'whitespace', 'content', 'whitespace']
    assert res[1].chunk == '\n'
    assert res[3].chunk == '\n'


def test__recursive__lex_filelike():
    # Test iterating through a file-like object
    rl = RecursiveLexer()
    # Specify explicitly a *unicode* string for python 2
    f = io.StringIO(u"Select\n   *\nFROM tbl\n")
    res = rl.lex_file_obj(f)
    assert res.string_list() == ['Select', '\n', '   ', '*', '\n', 'FROM', ' ', 'tbl', '\n']
    assert res.context_list() == [
        'content', 'whitespace', 'whitespace', 'content',
        'whitespace', 'content', 'whitespace', 'content',
        'whitespace']


def test__recursive__lex_file_basic():
    # Test iterating through a file object
    rl = RecursiveLexer()
    with open('test/fixtures/lexer/basic.sql') as f:
        res = rl.lex_file_obj(f)
        assert len(res) == 17
        assert res[0].chunk == 'SELECT'
        assert res[-1].chunk == '\n'


def test__recursive__lex_file_inlinecomment():
    # Check we can deal with block comments in line
    rl = RecursiveLexer()
    with open('test/fixtures/lexer/inline_comment.sql') as f:
        res = rl.lex_file_obj(f)
        # check that the inline comment arrives whole
        assert "-- This is an inline comment" in res.string_list()
        # The second is more tricky because it contains a quote
        assert "-- Sometimes they're on a new line" in res.string_list()


def test__recursive__lex_file_blockcomment():
    # Check we can deal with block comments in line
    rl = RecursiveLexer()
    with open('test/fixtures/lexer/block_comment.sql') as f:
        res = rl.lex_file_obj(f)
        # Check we get the block comment whole
        assert "/* Block comment with ending */" in res.string_list()
        # Check we get the field after the comment
        assert "a.something" in res.string_list()
