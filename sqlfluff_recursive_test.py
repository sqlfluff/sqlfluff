""" The Test file for SQLFluff """

from sqlfluff import CharMatchPattern, RecursiveLexer, PositionedChunk, ChunkString

# ############## Matchers
def test__charmatch__basic():
    cmp = CharMatchPattern('s')
    s = 'aefalfuinsefuynlsfa'
    assert cmp.first_match_pos(s) == 9


def test__charmatch__none():
    cmp = CharMatchPattern('s')
    s = 'aefalfuin^efuynl*fa'
    assert cmp.first_match_pos(s) == None


# ############## LEXER TESTS
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


# short term disabled test
def atest__recursive__comment_a():
    # This test requires recursion
    rl = RecursiveLexer()
    # The whitespace on the end of a comment should be it's own chunk
    pc = PositionedChunk('SELECT    -- Testing Comment\n', 0, 1)
    res, context = rl.lex(pc)
    assert res.content_list() == ['content', 'whitespace', 'comment', 'whitespace']
    assert res[3].content == '\n'
