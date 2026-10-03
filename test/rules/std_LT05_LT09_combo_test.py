"""Tests the combination of LT05 and LT09.

LT05: no long lines
LT09: single selects should be on SELECT line
"""

import pytest

import sqlfluff
from sqlfluff.core import FluffConfig


def test__rules__std_LT05_LT09_long_line_lint():
    """Verify a long line that causes a clash between LT05 and LT09 is not changed."""
    sql = (
        "SELECT\n1000000000000000000000000000000000000000000000000000000000000000000000"
        "000000000000000000000000000000\n"
    )
    result = sqlfluff.lint(sql)
    assert "LT05" in [r["code"] for r in result]
    assert "LT09" in [r["code"] for r in result]


def test__rules__std_LT05_LT09_long_line_fix():
    """Verify clash between LT05 & LT09 does not add multiple newlines (see #1424)."""
    sql = (
        "SELECT 10000000000000000000000000000000000000000000000000000000000000000000000"
        "00000000000000000000000000000\n"
    )
    result = sqlfluff.fix(sql)
    assert result == (
        "SELECT\n    100000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000\n"
    )


def test__rules__std_LT05_LT09_long_line_fix2():
    """Verify clash between LT05 & LT09 does not add multiple newlines (see #1424)."""
    sql = (
        "SELECT\n    100000000000000000000000000000000000000000000000000000000000000000"
        "0000000000000000000000000000000000\n"
    )
    result = sqlfluff.fix(sql)
    assert result == (
        "SELECT 10000000000000000000000000000000000000000000000000000000000000000000000"
        "00000000000000000000000000000\n"
    )


@pytest.mark.parametrize(
    "exclude_rules,expected",
    [
        # LT09 puts each select target on its own line, whatever the length.
        (
            None,
            "select\n    long_column_name1,\n    long_column_name2,\n"
            "    long_column_name3,\n    long_column_name4\nfrom tbl\n",
        ),
        (
            "LT09",
            "select\n    long_column_name1, long_column_name2,\n"
            "    long_column_name3, long_column_name4\nfrom tbl\n",
        ),
    ],
)
def test__rules__std_LT05_LT09_list_wrapping_fill(exclude_rules, expected):
    """Verify how LT09 interacts with list_wrapping = fill for select targets."""
    sql = (
        "select long_column_name1, long_column_name2, long_column_name3, "
        "long_column_name4\nfrom tbl\n"
    )
    configs = {
        "core": {"dialect": "ansi", "max_line_length": 45},
        "indentation": {"list_wrapping": "fill"},
    }
    if exclude_rules:
        configs["core"]["exclude_rules"] = exclude_rules
    result = sqlfluff.fix(sql, config=FluffConfig(configs=configs))
    assert result == expected
    # A second fix changes nothing.
    assert sqlfluff.fix(result, config=FluffConfig(configs=configs)) == expected
