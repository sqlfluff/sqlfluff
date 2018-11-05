""" The Test file for SQLFluff """

from sqlfluff.rules.std import load_standard_set
from sqlfluff.chunks import PositionedChunk


# ############## STD RULES TESTS
def test__rules__std__L001():
    rs = load_standard_set()
    c = PositionedChunk('     \n', 10, 20, 'whitespace')
    assert any([v.rule.code == 'L001' for v in rs.evaluate(c)])


def test__rules__std__L002():
    rs = load_standard_set()
    c = PositionedChunk('    \t    \t    ', 0, 20, 'whitespace')
    assert any([v.rule.code == 'L002' for v in rs.evaluate(c)])


def test__rules__std__L003():
    rs = load_standard_set()
    c = PositionedChunk('     ', 0, 20, 'whitespace')
    assert any([v.rule.code == 'L003' for v in rs.evaluate(c)])
