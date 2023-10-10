"""Test the string helpers."""

import pytest

from sqlfluff.core.string_helpers import findall


@pytest.mark.parametrize(
    "mainstr,substr,positions",
    [
        ("", "", []),
        ("a", "a", [0]),
        ("foobar", "o", [1, 2]),
        ("bar bar bar bar", "bar", [0, 4, 8, 12]),
    ],
)
def test__parser__helper_findall(mainstr, substr, positions):
    """Test _findall."""
    assert list(findall(substr, mainstr)) == positions
