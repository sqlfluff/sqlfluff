""" The Test file for SQLFluff """

import pytest
import six
import logging

from sqlfluff.parser.base import TerminalRule, Dialect, Rule, Node, sqlfluffParseError
from sqlfluff.parser.base import ZeroOrOne, OneOf, Seq, ZeroOrMore, OneOrMore, PositionedString, AnyOf


# ############## String TESTS
def test__parser__posstring_a():
    """ check string popping without newlines """
    s = PositionedString('abcdef')
    ns = s.popleft(3)
    assert ns.s == 'abc'
    assert ns.col_no == 1
    assert ns.line_no == 1
    assert s.s == 'def'
    assert s.col_no == 4
    assert s.line_no == 1


def test__parser__posstring_b():
    """ check string popping with newlines """
    s = PositionedString('ab\nc\ndef')
    ns = s.popleft(6)
    assert ns.s == 'ab\nc\nd'
    assert s.s == 'ef'
    assert s.col_no == 2
    assert s.line_no == 3


def test__parser__posstring_repr():
    assert isinstance(repr(PositionedString('ab\nc\ndef')), six.string_types)


# ############## Terminal TESTS
def test__parser__terminal():
    tr = TerminalRule('a', name='test', case_sensitive=False)
    m, r = tr.parse('ABC', None, None)
    assert m.s == 'A'
    assert m.token == 'test'
    assert r == 'BC'
    # Check formatting
    assert isinstance(repr(tr), six.string_types)


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
    d = Dialect(None, 'testA', [a])
    # Duplicate names
    with pytest.raises(ValueError):
        Dialect(None, 'testA', [a, a2])
    # Unknown Root Node
    with pytest.raises(ValueError):
        Dialect(None, 'failfail', [a2])
    # Check formatting
    assert isinstance(repr(d), six.string_types)


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
    # Check formatting
    assert isinstance(repr(a), six.string_types)


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


@pytest.mark.parametrize("test_input,expected_tokens,expected_residual", [
    ("BCD", ['b', 'c', 'd'], ''),
    ("BD", ['b', 'd'], ''),
    ("bDb", ['b', 'd', 'b'], ''),
])
def test__parser__rule_optional(test_input, expected_tokens, expected_residual):
    # Optional elements are ZeroOrOne
    a = Rule('a', Seq('b', ZeroOrOne('c'), 'd', ZeroOrOne('b')))
    b = TerminalRule(r'b')
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    dialect = Dialect(None, 'a', [a, b, c, d])
    # Parse with optional element
    tr, s = a.parse(test_input, tuple(), dialect)
    assert s == expected_residual
    assert isinstance(tr, Node)
    assert [nd.token for nd in tr.nodes] == expected_tokens


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


def assert_rule_parse(dialect, example, expected_residual='', rule=None, stack=None):
    if stack is None:
        stack = tuple()
    if rule:
        assert rule.parse(example, stack, dialect)[1] == expected_residual
    else:
        assert dialect.parse(example, stack)[1] == expected_residual


def assert_rule_fail(dialect, example, rule=None, stack=None):
    if stack is None:
        stack = tuple()
    if rule:
        with pytest.raises(sqlfluffParseError):
            rule.parse(example, stack, dialect)
    else:
        with pytest.raises(sqlfluffParseError):
            dialect.parse(example, stack)


def assert_rule_result(dialect, example, rule=None, stack=None, success=True, expected_residual=''):
    if success:
        assert_rule_parse(dialect=dialect, example=example, rule=rule,
                          stack=stack, expected_residual=expected_residual)
    else:
        assert_rule_fail(dialect=dialect, example=example, rule=rule, stack=stack)


@pytest.fixture(scope="module")
def token_dialect():
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    e = TerminalRule(r'e')
    dialect = Dialect(None, 'c', [c, d, e])
    return dialect


@pytest.mark.parametrize("example,success", [
    ('ccdd', True),
    ('cddd', True),
    ('cded', True),
    ('ccd', False),
    ('cde', False),
    ('cd', False),
    ('cdded', False)
])
def test__parser__rule_options_nested(token_dialect, example, success):
    # Defining a complex rule with nested components.
    r = Rule('a', Seq('c', OneOf(Seq('c', 'd'), Seq('d', OneOf('d', 'e'))), 'd'))
    assert_rule_result(dialect=token_dialect, example=example, rule=r, success=success)


@pytest.mark.parametrize("example,success,remainder", [
    ('cdcdcdcdcdcdcd', True, ''),
    ('cdcecdcecdce', True, ''),
    ('cececececece', True, ''),
    ('cd', True, ''),
    ('', True, ''),
    ('cde', True, 'e')
])
def test__parser__rule_zeroormore(token_dialect, example, success, remainder):
    # Defining a complex rule with nested components.
    r = Rule('a', ZeroOrMore('c', OneOf('d', 'e')))
    assert_rule_result(dialect=token_dialect, example=example, rule=r,
                       success=success, expected_residual=remainder)


@pytest.mark.parametrize("example,success,remainder", [
    ('cd', True, ''),
    ('cdcdcdcdcdcdcd', True, ''),
    ('cdcecdcecdce', True, ''),
    ('cececececece', True, ''),
    ('c', False, ''),
    ('cde', True, 'e')
])
def test__parser__rule_oneormore(token_dialect, example, success, remainder):
    # Defining a complex rule with nested components.
    r = Rule('a', OneOrMore('c', OneOf('d', 'e')))
    assert_rule_result(dialect=token_dialect, example=example, rule=r,
                       success=success, expected_residual=remainder)


@pytest.mark.parametrize("example,success", [
    ('cdeedddeddedc', True), ('cec', True), ('cdc', True),
    ('c', False), ('d', False), ('e', False), ('cc', False)
])
def test__parser__rule_anyof(caplog, token_dialect, example, success):
    # We want to see debug info for this test
    caplog.set_level(logging.DEBUG)
    # Defining a complex rule with nested components.
    r = Rule('a', Seq('c', AnyOf('d', 'e'), 'c'))
    assert_rule_result(dialect=token_dialect, example=example, rule=r,
                       success=success)


def test__parser__rule_reconstruct(caplog):
    """ Check we can reconstruct the string properly after deconstruction """
    # We want to see debug info for this test
    caplog.set_level(logging.DEBUG)
    # Defining a complex rule with nested components.
    a = Rule('a', AnyOf('d', 'e'))
    d = TerminalRule(r'd')
    e = TerminalRule(r'e')
    dialect = Dialect(None, 'a', [a, d, e])
    test_case = 'deedddedded'
    nd, _ = dialect.parse(test_case, tuple())
    assert nd.reconstruct() == test_case
