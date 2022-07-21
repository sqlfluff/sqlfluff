"""Tests the python routines within L003."""
import pytest

from sqlfluff.rules.L003 import Rule_L003, _Desc


@pytest.mark.parametrize(
    "indent_unit,num,tab_space_size,result",
    [
        ("space", 3, 2, "      "),
        ("tab", 3, 2, "\t\t\t"),
    ],
)
def test__rules__std_L003_make_indent(indent_unit, num, tab_space_size, result):
    """Test Rule_L003._make_indent."""
    res = Rule_L003._make_indent(
        num=num, indent_unit=indent_unit, tab_space_size=tab_space_size
    )
    assert res == result


def test__rules__std_L003_make_indent_invalid_param():
    """Test Rule_L003._make_indent with invalid indent_unit parameter."""
    with pytest.raises(ValueError):
        Rule_L003._make_indent(indent_unit="aaa")


class ProtoSeg:
    """Proto Seg for testing."""

    def __init__(self, raw):
        self.raw = raw

    def is_type(self, *seg_type):
        """Is this segment (or its parent) of the given type."""
        return False


@pytest.mark.parametrize(
    "tab_space_size,segments,result",
    [
        # Integer examples
        (3, [ProtoSeg("      ")], 6),
        (2, [ProtoSeg("\t\t")], 4),
    ],
)
def test__rules__std_L003_indent_size(tab_space_size, segments, result):
    """Test Rule_L003._indent_size."""
    res = Rule_L003._indent_size(segments=segments, tab_space_size=tab_space_size)
    assert res == result


@pytest.mark.parametrize(
    "expected,found,compared_to,has_partial_indent,expected_message",
    [
        (
            1,
            1,
            4,
            True,
            "Expected 1 indentation, found more than 1 [compared to line 04]",
        ),
        (
            2,
            1,
            10,
            False,
            "Expected 2 indentations, found 1 [compared to line 10]",
        ),
        (
            2,
            1,
            11,
            True,
            "Expected 2 indentations, found less than 2 [compared to line 11]",
        ),
    ],
)
def test__rules__std_L003_desc(
    expected, found, compared_to, has_partial_indent, expected_message
):
    """Test Rule_L003 error description."""
    assert _Desc(expected, found, compared_to, has_partial_indent) == expected_message
