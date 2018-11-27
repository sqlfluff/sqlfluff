""" The Test file for SQLFluff """

# from six import StringIO
import pytest

from sqlfluff.parser.base import Token, SyntaxRule, Dialect, TokenChunk


# ############## PARSER TESTS
# ########## Token tests
def test__token__match_a():
    """ basic token matching """
    t = Token(r'bl')
    assert t.match('black') == 'bl'


def test__token__match_b():
    """ case token matching """
    t = Token(r'bl')
    assert t.match('BLACK') == 'BL'


def test__token__match_c():
    """ case token matching """
    t = Token(r'bl', case_sensitive=True)
    assert t.match('BLACK') is None


# ########## Rule tests (make sure that invalid rules are caught)
def test__rule__validate():
    SyntaxRule.validate_sequence(['a'])
    SyntaxRule.validate_sequence([['a']])
    SyntaxRule.validate_sequence([set(['a', 'b']), 'd'])
    SyntaxRule.validate_sequence([('a',)])
    with pytest.raises(AssertionError):
        SyntaxRule.validate_sequence('a')
    with pytest.raises(AssertionError):
        SyntaxRule.validate_sequence([[['a']]])
    with pytest.raises(AssertionError):
        SyntaxRule.validate_sequence(['a', 2])
    with pytest.raises(AssertionError):
        SyntaxRule.validate_sequence(['a', ['c', 'd']])


# ########## Dialect tests
test_dialect = Dialect(
    name=None, description=None,
    tokens=[
        Token(pattern=r'a'),
        Token(pattern=r'b'),
        Token(pattern=r'c', syntax=False)
    ],
    syntax_rules=[
        SyntaxRule(name='bar', sequence=['a', 'b', ['a']]),
        SyntaxRule(name='foo', sequence=['bar', 'b'])
    ],
    root_element='foo'
)


def test__dialect__simple():
    """ Simple Dialect Matching """
    d = test_dialect
    # Single token matching
    assert d._match_token('BAB', 'b') == 'B'
    assert d._match_token('BAB', 'a') is None
    # Multi Token Matching
    assert d._match_tokens('BAB', ['a', 'b']) == {'b': 'B'}
    # All Token Matching
    assert d._match_all_tokens('BAB') == {'b': 'B'}
    # Rule Matching
    assert d._match_rule('BAB', 'a') == {}
    assert d._match_rule('BAB', 'b') == {(('b', True),): 'B'}
    assert d._match_rule('BAB', 'bar') == {}
    assert d._match_rule('ABA', 'bar') == {(('bar', 0), ('a', True)): 'A'}


def test__dialect__deeper():
    """ Dialect matching with deeper rules """
    d = test_dialect
    # Rule Matching
    assert d._match_rule('BAB', 'foo') == {}
    assert d._match_rule('ABA', 'foo') == {(('foo', 0), ('bar', 0), ('a', True)): 'A'}
    # And via the root element
    assert d.match_root_element('ABA') == {(('foo', 0), ('bar', 0), ('a', True)): 'A'}


def test__dialect__non_syntax():
    """ Dialect matching with non syntax """
    d = test_dialect
    # Rule Matching
    assert d._match_rule('CBAB', 'bar') == {}
    assert d._match_rule('CABA', 'foo') == {}
    # Non Syntax Matching
    assert d.match_non_syntax('CABA') == {(('c', False),): 'C'}
    # And via the root element
    assert d.match_root_element('CABA') == {(('c', False),): 'C'}


def test__dialect__fully_matched():
    """ Test the fully matched detection """
    d = test_dialect
    # Match some terminals
    assert d._is_fully_matched('a', (('a', True),)) == 'FullyMatched'
    assert d._is_fully_matched('a', (('c', False),)) == 'Unmatched'
    # Match some rules
    assert d._is_fully_matched('bar', (('bar', 0), ('a', True))) == 'Unmatched'
    assert d._is_fully_matched('bar', (('bar', 2), ('a', True))) == 'FullyMatched'
    assert d._is_fully_matched('foo', (('foo', 1), ('b', True))) == 'FullyMatched'


def test__dialect__pop_token():
    """ Dialect matching with token popping """
    d = test_dialect
    # Check without any existing stack (for a non-syntax token)
    expected_chunk_token = TokenChunk('C', 1, 1, stack=(('c', False),))
    assert d.pop_token('CBAB', 1, 1) == [(expected_chunk_token, 'BAB')]
    # Check without any existing stack (for a syntax token)
    expected_stack_position = (('foo', 0), ('bar', 0), ('a', True))
    expected_chunk_token = TokenChunk('A', 1, 1, stack=expected_stack_position)
    assert d.pop_token('ABCD', 1, 1) == [(expected_chunk_token, 'BCD')]
    # Check with an existing stack (The stack defines where in the rules we are)
    # For a Syntax Token
    expected_new_stack_position = (('foo', 0), ('bar', 1), ('b', True))
    expected_chunk_token = TokenChunk('B', 2, 1, stack=expected_new_stack_position)
    assert d.pop_token('BAB', 2, 1, stack_pos=expected_stack_position) == [(expected_chunk_token, 'AB')]
    # For a non-syntax token
    # # expected_chunk_token = TokenChunk('C', 2, 1, stack=(('c', False),))
    # # assert d.pop_token('CAB', 2, 1, stack_pos=expected_stack_position) == [(expected_chunk_token, 'AB')]
