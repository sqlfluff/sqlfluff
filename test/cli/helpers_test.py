"""The Test file for CLI helpers."""

import pytest

from sqlfluff.cli.helpers import colorize, cli_table, wrap_elem, wrap_field, pad_line
from sqlfluff.core.enums import Color


def test__cli__helpers__colorize():
    """Test ANSI colouring."""
    assert colorize("foo", Color.red) == "\u001b[31mfoo\u001b[0m"


def test__cli__helpers__cli_table():
    """Test making tables."""
    vals = [("a", 3), ("b", "c"), ("d", 4.7654), ("e", 9)]
    txt = cli_table(vals, col_width=7, divider_char="|", label_color=None)
    # NB: No trailing newline
    assert txt == "a:    3|b:    c\nd: 4.77|e:    9"


@pytest.mark.parametrize(
    "in_str,length,res",
    [
        ("abc", 5, ["abc"]),
        # Space wrap test
        ("how now brown cow", 10, ["how now", "brown cow"]),
        # Harder wrap test
        ("A hippopotamus came for tea", 10, ["A hippopot", "amus came", "for tea"]),
        # Harder wrap test, with a newline.
        ("A hippopotamus\ncame for tea", 10, ["A hippopot", "amus came", "for tea"]),
    ],
)
def test__cli__helpers__wrap_elem(in_str, length, res):
    """Test wrapping."""
    str_list = wrap_elem(in_str, length)
    assert str_list == res


def test__cli__helpers__wrap_field_a():
    """Test simple wrapping."""
    dct = wrap_field("abc", "How Now Brown Cow", width=40)
    assert dct["label_list"] == ["abc"]
    assert dct["val_list"] == ["How Now Brown Cow"]
    assert "sep_char" in dct
    assert dct["lines"] == 1
    assert dct["label_width"] == 3


def test__cli__helpers__wrap_field_b():
    """Test simple wrapping with overlap avoidance."""
    dct = wrap_field("abc", "How Now Brown Cow", width=23)
    assert dct["label_list"] == ["abc"]
    assert dct["val_list"] == ["How Now Brown Cow"]
    assert dct["label_width"] == 3


def test__cli__helpers__wrap_field_c():
    """Test simple wrapping."""
    dct = wrap_field("how now brn cow", "How Now Brown Cow", width=25)
    assert dct["label_list"] == ["how now", "brn cow"]
    assert dct["label_width"] == 7
    assert dct["val_list"] == ["How Now Brown", "Cow"]
    assert dct["lines"] == 2


def test__cli__helpers__pad_line():
    """Test line padding."""
    assert pad_line("abc", 5) == "abc  "
    assert pad_line("abcdef", 10, align="right") == "    abcdef"
