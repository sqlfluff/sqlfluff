import sqlfluff
from sqlfluff.core import FluffConfig, Linter


def test__rules__std_L016_L036_long_line_lint():
    """Verify that a long line that causes a clash between L016 and L036 is not changed."""
    sql = "SELECT\n100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\n"
    result = sqlfluff.lint(sql)
    assert "L016" in [r["code"] for r in result]
    assert "L036" in [r["code"] for r in result]


def test__rules__std_L016_L036_long_line_fix():
    """Verify that a long line that causes a clash between L016 and L036 does not add multiple newlines (see #1424)."""
    sql = "SELECT 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\n"
    result = sqlfluff.fix(sql)
    assert (
        result
        == "SELECT\n    100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\n"
    )


def test__rules__std_L016_L036_long_line_fix2():
    """Verify that a long line that causes a clash between L016 and L036 does not add multiple newlines (see #1424)."""
    sql = "SELECT\n    100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\n"
    result = sqlfluff.fix(sql)
    assert (
        result
        == "SELECT 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\n"
    )
