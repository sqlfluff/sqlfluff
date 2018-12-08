""" The Test file for SQLFluff """

import pytest
import six
import logging

from sqlfluff.parser.base import TerminalRule, Dialect, Rule, Node, sqlfluffParseError, Terminal
from sqlfluff.parser.base import ZeroOrOne, OneOf, Seq, ZeroOrMore, OneOrMore, PositionedString, AnyOf


@pytest.fixture(scope="module")
def token_dialect():
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    e = TerminalRule(r'e')
    dialect = Dialect(None, 'c', [c, d, e])
    return dialect


@pytest.fixture(scope="module")
def simple_dialect():
    a = Rule('a', Seq('b', 'c'))
    b = TerminalRule(r'b')
    c = TerminalRule(r'c')
    dialect = Dialect(None, 'a', [a, b, c])
    return dialect


# ############## String TESTS
@pytest.mark.parametrize("example", ['abcdef', 'ab\nc\ndef', '\n\n\n\n\nefBLAH'])
@pytest.mark.parametrize("offset", [1, 2, 3, 5])
def test__parser__posstring(example, offset):
    example_string = PositionedString(example)
    # Check type of repr
    assert isinstance(repr(example_string), six.string_types)
    # str function
    assert str(example_string) == example
    # check equality assertions (both with the raw string and another PositionedString)
    assert example_string == example
    assert example_string == PositionedString(example)
    # Test splitting
    left_string = example_string.popleft(offset)
    # Check the left side of the deal
    assert str(left_string) == example[:offset]
    assert left_string.col_no == 1
    assert left_string.line_no == 1
    # Check the right side of the deal
    assert str(example_string) == example[offset:]
    if '\n' in example[:offset]:
        assert example_string.col_no == len(example[:offset].split('\n')[-1]) + 1
    else:
        assert example_string.col_no == len(example[:offset]) + 1
    assert example_string.line_no == example[:offset].count('\n') + 1


# ############## Terminal TESTS
def test__parser__terminal():
    tr = TerminalRule('a', name='test', case_sensitive=False)
    m, r = tr.parse('ABC', None, None)
    assert m.asstring() == 'A'
    assert m.name == 'test'
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
def test__parser__rule(simple_dialect):
    """ Parsing via a rule """
    # Get the a rule
    a = simple_dialect.get_rule('a')
    # Parse by rule directly
    tr, s = a.parse('BCfoo', dialect=simple_dialect)
    assert s == 'foo'  # Check we catch the remainder properly
    assert isinstance(tr, Node)
    assert tr.nodes[0].name == 'b'
    assert tr.nodes[1].name == 'c'
    assert str(tr.nodes[0]) == 'B'
    assert str(tr.nodes[1]) == 'C'
    # Check formatting
    assert isinstance(repr(tr), six.string_types)


def test__parser__rule_terminal(simple_dialect):
    """ Parsing via a terminal """
    # Get the a rule
    b = simple_dialect.get_rule('b')
    # Parse by rule directly
    tr, s = b.parse('BCfoo', dialect=simple_dialect)
    assert s == 'Cfoo'  # Check we catch the remainder properly
    assert isinstance(tr, Terminal)
    assert tr.name == 'b'
    assert str(tr) == 'B'
    # Check formatting
    assert isinstance(repr(tr), six.string_types)


def test__parser__rule_astuple(simple_dialect):
    """ Same test as above, but testing astuple """
    # Get the a rule
    a = simple_dialect.get_rule('a')
    # Parse by rule directly
    tr, _ = a.parse('BCfoo', dialect=simple_dialect)
    assert tr.astuple() == ('a', (('b', 'B'), ('c', 'C')))


def test__parser__dialect_parse(simple_dialect):
    """ Parsing via the dialect """
    # Call rule via root_rule
    tr, s = simple_dialect.parse('BCfoo')
    assert s == 'foo'  # Check we catch the remainder properly
    assert isinstance(tr, Node)
    assert tr.nodes[0].name == 'b'
    assert tr.nodes[1].name == 'c'
    assert str(tr.nodes[0]) == 'B'
    assert str(tr.nodes[1]) == 'C'
    # Check that formatting doesn't error
    assert isinstance(tr.prnt(), str)


def test__parser__dialect_parse_node_tuple_set(simple_dialect):
    """ Check that the node_tuple_set works """
    # Call rule via root_rule
    tr, _ = simple_dialect.parse('BCfoo')
    assert tr.node_tuple_set() == {('a', 'BC'), ('b', 'B'), ('c', 'C')}


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
    tr, s = a.parse(test_input, dialect=dialect)
    assert s == expected_residual
    assert isinstance(tr, Node)
    assert tr.tokens() == expected_tokens


def test__parser__rule_nested():
    # Optional elements are shown in brackets
    a = Rule('a', Seq('b', ZeroOrOne('c'), 'd', ZeroOrOne('b')))
    b = Rule('b', Seq('d', ZeroOrOne('c'), 'd'))
    c = TerminalRule(r'c')
    d = TerminalRule(r'd')
    dialect = Dialect(None, 'a', [a, b, c, d])
    # Parse with optional element
    tr, s = a.parse('DCDCDDD', dialect=dialect)
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
    tr, s = a.parse('CCDD', dialect=dialect)
    assert s == 'D'
    assert tr.astuple() == (
        'a', (
            ('c', 'C'),
            ('c', 'C'),
            ('d', 'D')
        )
    )
    # Parse with something intentionally not leftover
    tr, s = a.parse('CDD', dialect=dialect)
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
        assert rule.parse(example, rule_stack=stack, dialect=dialect)[1] == expected_residual
    else:
        assert dialect.parse(example, rule_stack=stack)[1] == expected_residual


def assert_rule_fail(dialect, example, rule=None, stack=None):
    if stack is None:
        stack = tuple()
    if rule:
        with pytest.raises(sqlfluffParseError):
            rule.parse(example, rule_stack=stack, dialect=dialect)
    else:
        with pytest.raises(sqlfluffParseError):
            dialect.parse(example, rule_stack=stack)


def assert_rule_result(dialect, example, rule=None, stack=None, success=True, expected_residual=''):
    if success:
        assert_rule_parse(dialect=dialect, example=example, rule=rule,
                          stack=stack, expected_residual=expected_residual)
    else:
        assert_rule_fail(dialect=dialect, example=example, rule=rule, stack=stack)


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


def test__parser__rule_asstring(caplog):
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
    assert nd.asstring() == test_case
