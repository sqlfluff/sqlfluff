""" The Test file for SQLFluff """

import pytest

from sqlfluff.parser.base2 import TerminalRule, Dialect, Rule, Node


# ############## Terminal TESTS
def test__parser__terminal():
    tr = TerminalRule('a', name='test', case_sensitive=False)
    m, r = tr.parse('ABC', None, None)
    assert m.s == 'A'
    assert m.token == 'test'
    assert r == 'BC'


# ############## Dialect TESTS
def test__dialect__get_rule():
    a = TerminalRule(r'a', name='testA', case_sensitive=False)
    b = TerminalRule(r'b', name='testB', case_sensitive=False)
    d = Dialect(None, 'testA', [a, b])
    assert d.get_rule('testA') is a
    assert d.get_rule('testB') is b


def test__dialect__validation():
    a = TerminalRule(r'a', name='testA', case_sensitive=False)
    a2 = TerminalRule(r'b', name='testA', case_sensitive=False)
    # Check simple passes
    Dialect(None, 'testA', [a])
    # Duplicate names
    with pytest.raises(ValueError):
        Dialect(None, 'testA', [a, a2])
    # Unknown Root Node
    with pytest.raises(ValueError):
        Dialect(None, 'failfail', [a2])


# ############## Rule TESTS
def test__parser__rule():
    a = Rule('a', ['b', 'c'])
    b = TerminalRule(r'b')
    c = TerminalRule(r'c')
    dialect = Dialect(None, 'a', [a, b, c])
    # Parse by rule directly
    tr, s = a.parse('BCfoo', tuple(), dialect)
    assert s == 'foo'  # Check we catch the remainder properly
    assert isinstance(tr, Node)
    assert tr.nodes[0].token == 'b'
    assert tr.nodes[1].token == 'c'
    assert tr.nodes[0].s == 'B'
    assert tr.nodes[1].s == 'C'


def test__parser__dialect_parse():
    a = Rule('a', ['b', 'c'])
    b = TerminalRule(r'b')
    c = TerminalRule(r'c')
    dialect = Dialect(None, 'a', [a, b, c])
    # Call rule via root_rule
    tr, s = dialect.parse('BCfoo')
    assert s == 'foo'  # Check we catch the remainder properly
    assert isinstance(tr, Node)
    assert tr.nodes[0].token == 'b'
    assert tr.nodes[1].token == 'c'
    assert tr.nodes[0].s == 'B'
    assert tr.nodes[1].s == 'C'
    # Check that formatting doesn't error
    assert isinstance(tr.prnt(), str)


def test__parser__rule_optional():
    # Optional elements are shown in brackets
    a = Rule('a', ['b', ['c'], 'd', ['b']])
    b = TerminalRule(r'b')
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    dialect = Dialect(None, 'a', [a, b, c, d])
    # Parse with optional element
    tr, s = a.parse('BCD', tuple(), dialect)
    assert s == ''
    assert isinstance(tr, Node)
    assert tr.nodes[0].token == 'b'
    assert tr.nodes[1].token == 'c'
    assert tr.nodes[2].token == 'd'
    # Parse without optional element
    tr, s = a.parse('BD', tuple(), dialect)
    assert s == ''
    assert isinstance(tr, Node)
    assert tr.nodes[0].token == 'b'
    assert tr.nodes[1].token == 'd'
    # Parse with optional element at the end
    tr, s = a.parse('bDb', tuple(), dialect)
    assert s == ''
    assert isinstance(tr, Node)
    assert tr.nodes[0].token == 'b'
    assert tr.nodes[1].token == 'd'
    assert tr.nodes[2].token == 'b'

