"""Tests the python routines within RF02."""

import sqlfluff


def test__rules__std_RF02_wildcard_single_count():
    """Verify that RF02 is only raised once for wildcard (see issue #1973)."""
    sql = """
        SELECT *
        FROM foo
        INNER JOIN bar;
    """
    result = sqlfluff.lint(sql)
    assert "RF02" in [r["code"] for r in result]
    assert [r["code"] for r in result].count("RF02") == 1
