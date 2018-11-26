""" The Test file for SQLFluff """

from six import StringIO

from sqlfluff.parser.base import Token, SyntaxRule, Dialect


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
