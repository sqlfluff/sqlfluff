"""Tests the python routines within L009."""

import sqlfluff


def test__rules__std_L009_single_final_newline():
    """Verify that L020 returns the correct error message for one duplicate table aliases occur one times."""
    sql = """
        SELECT
            a.pk
        FROM table_1 AS a
        JOIN table_2 AS a ON a.pk = a.pk\n"""
    result = sqlfluff.lint(sql)
    assert "L009" not in [r["code"] for r in result]
    assert [r["code"] for r in result].count("L009") == 0


def test__rules__std_L009_no_final_newline():
    """Verify that L009 returns the correct error message for a missing final newline."""
    sql = """
        SELECT
            a.pk
        FROM table_1 AS a
        JOIN table_2 AS a ON a.pk = a.pk"""
    result = sqlfluff.lint(sql)
    assert "L009" in [r["code"] for r in result]
    assert [r["code"] for r in result].count("L009") == 1


def test__rules__std_L009_multiple_final_newlines():
    """Verify that L009 returns the correct error message for multiple final newlines."""
    sql = """
        SELECT
            a.pk
        FROM table_1 AS a
        JOIN table_2 AS a ON a.pk = a.pk\n\n"""
    result = sqlfluff.lint(sql)
    assert "L009" in [r["code"] for r in result]
    assert [r["code"] for r in result].count("L009") == 1
