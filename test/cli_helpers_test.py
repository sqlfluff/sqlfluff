""" The Test file for CLI helpers """

from sqlfluff.cli.helpers import colorize, cli_table


def test__cli__helpers__colorize():
    assert colorize('foo', 'red') == "\u001b[31mfoo\u001b[0m"


def test__cli__helpers__cli_table():
    vals = [('a', 3), ('b', 'c'), ('d', 4.7654), ('e', 9)]
    txt = cli_table(vals, col_width=6, divider_char='|', label_color=None)
    # NB: No trailing newline
    assert txt == 'a:   3|b:   c\nd:4.77|e:   9'
