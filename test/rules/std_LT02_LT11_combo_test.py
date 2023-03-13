"""Tests the combination of LT02 and LT11.

LT02: Indentation not consistent with previous lines
LT11: Set operators should be surrounded by newlines

Auto fix of LT11 does not insert correct indentation but just Newlines. It relies on
LT02 to sort out the indentation later. This is what is getting tested here.
"""

import sqlfluff


def test__rules__std_LT02_LT11_union_all_in_subquery_lint():
    """Verify a that LT11 reports lint errors in subqueries."""
    sql = (
        "SELECT * FROM (\n"
        "    SELECT 'g' UNION ALL\n"
        "    SELECT 'h'\n"
        "    UNION ALL SELECT 'j'\n"
        ")\n"
    )
    result = sqlfluff.lint(sql)

    assert "LT11" in [r["code"] for r in result]


def test__rules__std_LT02_LT11_union_all_in_subquery_fix():
    """Verify combination of rules LT02 and LT11 produces a correct indentation."""
    sql = (
        "SELECT c FROM (\n"
        "    SELECT 'g' UNION ALL\n"
        "    SELECT 'h'\n"
        "    UNION ALL SELECT 'j'\n"
        ")\n"
    )
    fixed_sql = (
        "SELECT c FROM (\n"
        "    SELECT 'g'\n"
        "    UNION ALL\n"
        "    SELECT 'h'\n"
        "    UNION ALL\n"
        "    SELECT 'j'\n"
        ")\n"
    )
    result = sqlfluff.fix(sql)
    assert result == fixed_sql
