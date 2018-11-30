""" The Test file for SQLFluff """

import pytest

from sqlfluff.parser.base2 import TerminalRule, Dialect, Rule, Node


# ############## Terminal TESTS
def test__parser__terminal():
    tr = TerminalRule('test', 'a', case_sensitive=False)
    m, r = tr.parse('ABC', None, None)
    assert m.s == 'A'
    assert m.token == 'test'
    assert r == 'BC'


# ############## Dialect TESTS
def test__dialect__get_rule():
    a = TerminalRule('testA', r'a', case_sensitive=False)
    b = TerminalRule('testB', r'b', case_sensitive=False)
    d = Dialect(None, 'testA', [a, b])
    assert d.get_rule('testA') is a
    assert d.get_rule('testB') is b


def test__dialect__validation():
    a = TerminalRule('testA', r'a', case_sensitive=False)
    a2 = TerminalRule('testA', r'b', case_sensitive=False)
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
    b = TerminalRule('b', r'b', case_sensitive=False)
    c = TerminalRule('c', r'c', case_sensitive=False)
    d = Dialect(None, 'a', [a, b, c])
    # Parse by rule directly
    tr, s = a.parse('BC', tuple(), d)
    assert s == ''
    assert isinstance(tr, Node)
    assert tr.nodes[0].token == 'b'
    assert tr.nodes[1].token == 'c'
    assert tr.nodes[0].s == 'B'
    assert tr.nodes[1].s == 'C'
