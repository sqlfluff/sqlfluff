""" The Test file for CLI helpers """

from sqlfluff.cli.helpers import colorize, cli_table, sum_dicts


def test__cli__helpers__colorize():
    assert colorize('foo', 'red') == "\u001b[31mfoo\u001b[0m"


def test__cli__helpers__cli_table():
    vals = [('a', 3), ('b', 'c'), ('d', 4.7654), ('e', 9)]
    txt = cli_table(vals, col_width=6, divider_char='|', label_color=None)
    # NB: No trailing newline
    assert txt == 'a:   3|b:   c\nd:4.77|e:   9'


def test__cli__helpers__sum_dicts():
    i = {}
    a = dict(a=3, b=123, f=876.321)
    b = dict(a=19, b=321.0, g=23478)
    r = dict(a=22, b=444.0, f=876.321, g=23478)
    assert sum_dicts(a, b) == r
    # Check the identity too
    assert sum_dicts(r, i) == r
