""" The Test file for SQLFluff """

import pytest

from sqlfluff.parser.base2 import TerminalRule, Dialect, Rule, Node, sqlfluffParseError, ZeroOrOne, OneOf, Seq, ZeroOrMore, OneOrMore


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
    a = Rule('a', Seq('b', 'c'))
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


def test__parser__rule_astuple():
    """ Same test as above, but testing astuple """
    a = Rule('a', Seq('b', 'c'))
    b = TerminalRule(r'b')
    c = TerminalRule(r'c')
    dialect = Dialect(None, 'a', [a, b, c])
    # Parse by rule directly
    tr, _ = a.parse('BCfoo', tuple(), dialect)
    assert tr.astuple() == ('a', (('b', 'B'), ('c', 'C')))


def test__parser__dialect_parse():
    a = Rule('a', Seq('b', 'c'))
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
    # Optional elements are ZeroOrOne
    a = Rule('a', Seq('b', ZeroOrOne('c'), 'd', ZeroOrOne('b')))
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


def test__parser__rule_nested():
    # Optional elements are shown in brackets
    a = Rule('a', Seq('b', ZeroOrOne('c'), 'd', ZeroOrOne('b')))
    b = Rule('b', Seq('d', ZeroOrOne('c'), 'd'))
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    dialect = Dialect(None, 'a', [a, b, c, d])
    # Parse with optional element
    tr, s = a.parse('DCDCDDD', tuple(), dialect)
    assert s == ''
    assert tr.astuple() == (
        'a', (
            ('b', (('d', 'D'), ('c', 'C'), ('d', 'D'))),
            ('c', 'C'),
            ('d', 'D'),
            ('b', (('d', 'D'), ('d', 'D')))
        )
    )


def test__parser__rule_options():
    # Elements where there are options are shown in {}
    a = Rule('a', Seq('c', OneOf('c', 'd'), 'd'))
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    dialect = Dialect(None, 'a', [a, c, d])
    # Parse with something intentionally leftover
    tr, s = a.parse('CCDD', tuple(), dialect)
    assert s == 'D'
    assert tr.astuple() == (
        'a', (
            ('c', 'C'),
            ('c', 'C'),
            ('d', 'D')
        )
    )
    # Parse with something intentionally not leftover
    tr, s = a.parse('CDD', tuple(), dialect)
    assert s == ''
    assert tr.astuple() == (
        'a', (
            ('c', 'C'),
            ('d', 'D'),
            ('d', 'D')
        )
    )


def generic_passing_failing_dialect_test(dialect, parsing_examples=[], failing_examples=[]):
    # Some examples that parse
    for example in parsing_examples:
        print("Example: {0}".format(example))
        assert dialect.parse(example, tuple())[1] == ''
    # Some example that shouldn't parse
    for example in failing_examples:
        print("Example: {0}".format(example))
        with pytest.raises(sqlfluffParseError):
            dialect.parse(example, tuple())


def test__parser__rule_options_nested():
    # Defining a complex rule with nested components.
    a = Rule('a', Seq('c', OneOf(Seq('c', 'd'), Seq('d', OneOf('d', 'e'))), 'd'))
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    e = TerminalRule(r'e')
    dialect = Dialect(None, 'a', [a, c, d, e])
    generic_passing_failing_dialect_test(
        dialect,
        parsing_examples=['ccdd', 'cddd', 'cded'],
        failing_examples=['ccd', 'cde', 'cd', 'cdded']
    )


def test__parser__rule_zeroormore():
    # Defining a complex rule with nested components.
    a = Rule('a', ZeroOrMore('c', OneOf('d', 'e')))
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    e = TerminalRule(r'e')
    dialect = Dialect(None, 'a', [a, c, d, e])
    generic_passing_failing_dialect_test(
        dialect,
        parsing_examples=['cdcdcdcdcdcdcd', 'cdcecdcecdce', 'cececececece', 'cd', '']
    )
    # Check a remainder example
    assert dialect.parse('cde', tuple())[1] == 'e'


def test__parser__rule_oneormore():
    # Defining a complex rule with nested components.
    a = Rule('a', OneOrMore('c', OneOf('d', 'e')))
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    e = TerminalRule(r'e')
    dialect = Dialect(None, 'a', [a, c, d, e])
    generic_passing_failing_dialect_test(
        dialect,
        parsing_examples=['cd', 'cdcdcdcdcdcdcd', 'cdcecdcecdce', 'cececececece'],
        failing_examples=['c']
    )
    # Check a remainder example
    assert dialect.parse('cde', tuple())[1] == 'e'
