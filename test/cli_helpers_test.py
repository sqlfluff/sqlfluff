""" The Test file for CLI helpers """

from sqlfluff.cli.helpers import colorize, cli_table, wrap_elem


def test__cli__helpers__colorize():
    assert colorize('foo', 'red') == "\u001b[31mfoo\u001b[0m"


def test__cli__helpers__cli_table():
    vals = [('a', 3), ('b', 'c'), ('d', 4.7654), ('e', 9)]
    txt = cli_table(vals, col_width=7, divider_char='|', label_color=None)
    # NB: No trailing newline
    assert txt == 'a:    3|b:    c\nd: 4.77|e:    9'


def test__cli__helpers__wrap_elem_a():
    """ Simple wrap test """
    str_list = wrap_elem('abc', 5)
    assert str_list == ['abc']


def test__cli__helpers__wrap_elem_b():
    """ Space wrap test """
    str_list = wrap_elem('how now brown cow', 10)
    assert str_list == ['how now', 'brown cow']


def test__cli__helpers__wrap_elem_c():
    """ Harder wrap test """
    str_list = wrap_elem('A hippopotamus came for tea', 10)
    assert str_list == ['A hippopot', 'amus came', 'for tea']


def test__cli__helpers__wrap_elem_d():
    """ Harder wrap test, with a newline """
    str_list = wrap_elem('A hippopotamus\ncame for tea', 10)
    assert str_list == ['A hippopot', 'amus came', 'for tea']
