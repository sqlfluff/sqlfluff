""" The Test file for SQLFluff """

from sqlfluff.rules.std import StandardRuleSet
from sqlfluff.chunks import PositionedChunk, ChunkString


# ############## STD RULES TESTS
def test__rules__std__L001():
    rs = StandardRuleSet()
    c = PositionedChunk('     \n', 10, 20, 'whitespace')
    assert any([v.rule.code == 'L001' for v in rs.evaluate(c)])


def test__rules__std__L002():
    rs = StandardRuleSet()
    c = PositionedChunk('    \t    \t    ', 0, 20, 'whitespace')
    assert any([v.rule.code == 'L002' for v in rs.evaluate(c)])


def test__rules__std__L003():
    rs = StandardRuleSet()
    c = PositionedChunk('     ', 0, 20, 'whitespace')
    assert any([v.rule.code == 'L003' for v in rs.evaluate(c)])


def test__rules__std__L004_whitespace():
    rl = StandardRuleSet.code_lookup('L004')
    ws_chars = rl.whitespace_chars('r4o4o4owii78w4w')
    assert ws_chars == set([])
    ws_chars = rl.whitespace_chars(' dsafk\tdsjk\n   \tsakldj')
    assert ws_chars == set([' ', '\t'])


def test__rules__std__L004():
    cs = ChunkString(
        PositionedChunk('    \n', 0, 20, 'whitespace'),
        PositionedChunk('\t\n', 0, 21, 'whitespace')
    )
    # Check individually, there's no errors
    # First (alone should not raise)
    rs = StandardRuleSet()
    vs = rs.evaluate(cs[0])
    assert not any([v.rule.code == 'L004' for v in vs])
    # Second (alone should not raise)
    rs = StandardRuleSet()
    vs = rs.evaluate(cs[1])
    assert not any([v.rule.code == 'L004' for v in vs])
    # Combined (which should raise an L004)
    rs = StandardRuleSet()
    vs = rs.evaluate_chunkstring(cs)
    assert any([v.rule.code == 'L004' for v in vs])


def test__rules__std__L005():
    # L005 is about spaces before commas
    cs = ChunkString(
        PositionedChunk('1', 0, 20, 'content'),
        PositionedChunk(' ', 0, 21, 'whitespace'),
        PositionedChunk(',', 0, 22, 'comma')
    )
    rs = StandardRuleSet()
    vs = rs.evaluate_chunkstring(cs)
    assert any([v.rule.code == 'L005' for v in vs])


def test__rules__std__L008():
    # L008 is about spaces after commas
    cs = ChunkString(
        PositionedChunk('1', 0, 20, 'content'),
        PositionedChunk(',', 0, 21, 'comma'),
        PositionedChunk('   ', 0, 22, 'whitespace'),
        PositionedChunk('2', 0, 23, 'content'),
        PositionedChunk('\n', 0, 24, 'whitespace'),
    )
    rs = StandardRuleSet()
    vs = rs.evaluate_chunkstring(cs)
    assert any([v.rule.code == 'L008' for v in vs])
