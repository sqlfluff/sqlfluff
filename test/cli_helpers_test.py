""" The Test file for CLI helpers """

from sqlfluff.cli.helpers import colorize, cli_table, wrap_elem, wrap_field, pad_line


def test__cli__helpers__colorize():
    assert colorize('foo', 'red') == u"\u001b[31mfoo\u001b[0m"


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


def test__cli__helpers__wrap_field_a():
    """ Simple wrap test """
    dct = wrap_field('abc', 'How Now Brown Cow', width=40)
    assert dct['label_list'] == ['abc']
    assert dct['val_list'] == ['How Now Brown Cow']
    assert 'sep_char' in dct
    assert dct['lines'] == 1
    assert dct['label_width'] == 3


def test__cli__helpers__wrap_field_b():
    """ Simple wrap test, but testing overlap allowance """
    dct = wrap_field('abc', 'How Now Brown Cow', width=23)
    assert dct['label_list'] == ['abc']
    assert dct['val_list'] == ['How Now Brown Cow']
    assert dct['label_width'] == 3


def test__cli__helpers__wrap_field_c():
    """ Simple wrap test """
    dct = wrap_field('how now brn cow', 'How Now Brown Cow', width=25)
    assert dct['label_list'] == ['how now', 'brn cow']
    assert dct['label_width'] == 7
    assert dct['val_list'] == ['How Now Brown', 'Cow']
    assert dct['lines'] == 2


def test__cli__helpers__pad_line():
    assert pad_line("abc", 5) == 'abc  '
    assert pad_line("abcdef", 10, align='right') == '    abcdef'
