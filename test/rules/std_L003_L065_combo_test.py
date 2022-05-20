"""Tests the combination of L003 and L065.

L003: Indentation not consistent with previous lines
L065: Set operators should be surrounded by newlines

Auto fix of L065 does not insert correct indentation but just Newlines. It relies on
L003 to sort out the indentation later. This is what is getting tested here.
"""

import sqlfluff


def test__rules__std_L003_L065_union_all_in_subquery_lint():
    """Verify a that L065 reports lint errors in subqueries."""
    sql = (
        "SELECT * FROM (\n"
        "    SELECT 'g' UNION ALL\n"
        "    SELECT 'h'\n"
        "    UNION ALL SELECT 'j'\n"
        ")\n"
    )
    result = sqlfluff.lint(sql)

    assert "L065" in [r["code"] for r in result]


def test__rules__std_L003_L065_union_all_in_subquery_fix():
    """Verify combination of rules L003 and L065 produces a correct indentation."""
    sql = (
        "SELECT * FROM (\n"
        "    SELECT 'g' UNION ALL\n"
        "    SELECT 'h'\n"
        "    UNION ALL SELECT 'j'\n"
        ")\n"
    )
    fixed_sql = (
        "SELECT * FROM (\n"
        "    SELECT 'g'\n"
        "    UNION ALL\n"
        "    SELECT 'h'\n"
        "    UNION ALL\n"
        "    SELECT 'j'\n"
        ")\n"
    )
    result = sqlfluff.fix(sql)
    assert result == fixed_sql
