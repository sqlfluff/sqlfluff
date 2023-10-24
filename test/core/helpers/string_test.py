"""Test the string helpers."""

import pytest

from sqlfluff.core.helpers.string import findall, split_comma_separated_string


@pytest.mark.parametrize(
    "mainstr,substr,positions",
    [
        ("", "", []),
        ("a", "a", [0]),
        ("foobar", "o", [1, 2]),
        ("bar bar bar bar", "bar", [0, 4, 8, 12]),
    ],
)
def test__helpers_string__findall(mainstr, substr, positions):
    """Test _findall."""
    assert list(findall(substr, mainstr)) == positions


@pytest.mark.parametrize(
    "raw_str, expected",
    [
        ("AL01,LT08,AL07", ["AL01", "LT08", "AL07"]),
        ("\nAL01,\nLT08,\nAL07,", ["AL01", "LT08", "AL07"]),
        (["AL01", "LT08", "AL07"], ["AL01", "LT08", "AL07"]),
    ],
)
def test__helpers_string__split_comma_separated_string(raw_str, expected):
    """Tests that string and lists are output correctly."""
    assert split_comma_separated_string(raw_str) == expected
