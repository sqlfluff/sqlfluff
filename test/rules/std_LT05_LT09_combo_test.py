"""Tests the combination of LT05 and LT09.

LT05: no long lines
LT09: single selects should be on SELECT line
"""

import sqlfluff


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
