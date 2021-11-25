"""Tests the python routines within L027."""

import sqlfluff


def test__rules__std_L027_wildcard_single_count():
    """Verify that L027 is only raised once for wildcard (see issue #1973)."""
    sql = """
        SELECT *
        FROM foo
        INNER JOIN bar;
    """
    result = sqlfluff.lint(sql)
    assert "L027" in [r["code"] for r in result]
    assert [r["code"] for r in result].count("L027") == 1
