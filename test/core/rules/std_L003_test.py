"""Tests the python routines within L003."""

import pytest

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.rules import get_ruleset
from sqlfluff.core.rules.std.L003 import Rule_L003
from sqlfluff.testing.rules import get_rule_from_set


@pytest.mark.parametrize(
    "test_elems,result",
    [
        # Unindented test examples
        (
            ["bar"],
            {
                1: {
                    "line_no": 1,
                    "indent_size": 0,
                    "indent_balance": 0,
                    "hanging_indent": None,
                    "clean_indent": False,
                },
            },
        ),
        (
            ["bar", "\n", "     ", "foo", "baar", " \t "],
            {
                1: {
                    "line_no": 1,
                    "indent_size": 0,
                    "indent_balance": 0,
                    "hanging_indent": None,
                    "clean_indent": False,
                },
                2: {
                    "line_no": 2,
                    "indent_size": 5,
                    "indent_balance": 0,
                    "hanging_indent": None,
                    "clean_indent": False,
                },
            },
        ),
        # Indented Test Example
        (
            ["bar", "<indent>", "\n", "    ", "foo", "<dedent>", "\n", "baar"],
            {
                1: {
                    "line_no": 1,
                    "indent_size": 0,
                    "indent_balance": 0,
                    "hanging_indent": None,
                    "clean_indent": False,
                },
                2: {
                    "line_no": 2,
                    "indent_size": 4,
                    # Balance of indents is 1 at the start of content
                    # of this line.
                    "indent_balance": 1,
                    "hanging_indent": None,
                    # It's a clean indent, because there was an indent
                    # token just before the previous newline.
                    "clean_indent": True,
                },
                3: {
                    "line_no": 3,
                    "indent_size": 0,
                    "indent_balance": 0,
                    "hanging_indent": None,
                    "clean_indent": False,
                },
            },
        ),
        # Hanging Test Example
        (
            ["bar", " ", "<indent>", "foo", "\n", "    ", "foo", "<dedent>"],
            {
                1: {
                    "line_no": 1,
                    "indent_size": 0,
                    "indent_balance": 0,
                    # It's a hanging indent possibility because there was an unresolved
                    # indent in the previous line before the end.
                    "hanging_indent": 4,
                    "clean_indent": False,
                },
                2: {
                    "line_no": 2,
                    "indent_size": 4,
                    "indent_balance": 1,
                    "hanging_indent": None,
                    "clean_indent": False,
                },
            },
        ),
    ],
)
def test__rules__std_L003_process_raw_stack(generate_test_segments, test_elems, result):
    """Test the _process_raw_stack function.

    Note: This test probably needs expanding. It doesn't
    really check enough of the full functionality.

    """
    cfg = FluffConfig()
    r = get_rule_from_set("L003", config=cfg)
    test_stack = generate_test_segments(test_elems)
    res = r._process_raw_stack(test_stack)
    print(res)
    # Verify structure
    assert isinstance(res, dict)
    assert all(isinstance(k, int) for k in res.keys())
    assert all(isinstance(v, dict) for v in res.values())
    # Check keys are all present
    assert all(
        v.keys()
        == {
            "line_no",
            "line_buffer",
            "indent_buffer",
            "indent_size",
            "indent_balance",
            "hanging_indent",
            "clean_indent",
        }
        for v in res.values()
    )
    # For testing purposes, we won't be checking the buffer fields
    for k in res:
        del res[k]["line_buffer"]
        del res[k]["indent_buffer"]
    assert res == result


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


class ProtoSeg:
    """Proto Seg for testing."""

    def __init__(self, raw):
        self.raw = raw


@pytest.mark.parametrize(
    "tab_space_size,segments,result",
    [
        # Integer examples
        (3, [ProtoSeg("      ")], 2),
        (2, [ProtoSeg("\t\t")], 2),
    ],
)
def test__rules__std_L003_indent_size(tab_space_size, segments, result):
    """Test Rule_L003._make_indent."""
    res = Rule_L003._indent_size(segments=segments, tab_space_size=tab_space_size)
    assert res == result


@pytest.mark.parametrize(
    "tab_space_size,segments,result",
    [
        # Integer examples
        (3, [ProtoSeg("      ")], 6),
        (2, [ProtoSeg("\t\t")], 4),
    ],
)
def test__rules__std_L003_indent_size(tab_space_size, segments, result):
    """Test Rule_L003._make_indent."""
    res = Rule_L003._indent_size(segments=segments, tab_space_size=tab_space_size)
    assert res == result
