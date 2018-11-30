""" The Test file for SQLFluff """

# from six import StringIO
import pytest

from sqlfluff.parser.base2 import TerminalRule


# ############## Terminal TESTS
def test__parser__terminal():
    tr = TerminalRule('test', 'a', case_sensitive=False)
    m, r = tr.parse('ABC', None, None)
    assert m.s == 'A'
    assert m.token == 'test'
    assert r == 'BC'
