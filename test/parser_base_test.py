""" The Test file for SQLFluff """

from six import StringIO

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


# ########## Dialect tests
test_dialect = Dialect(
    name=None, description=None,
    tokens=[
        Token(pattern=r'a'),
        Token(pattern=r'b'),
        Token(pattern=r'c', syntax=False)
    ],
    syntax_rules=[
        SyntaxRule(name='bar', sequence=['a', 'b', 'a']),
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


def test__dialect__pop_token():
    """ Dialect matching with non syntax """
    d = test_dialect
    chunk_token = TokenChunk('C', 1, 1, stack=(('c', False),))
    assert d.pop_token('CBAB', 1, 1) == [(chunk_token, 'BAB')]
