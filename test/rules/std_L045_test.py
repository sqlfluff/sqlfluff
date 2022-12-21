"""Tests the python routines within L045."""

import sqlfluff


def test__rules__std_L045_multiple_unused_ctes():
    """Verify that L045 returns multiple lint issues, one per unused CTE."""
    sql = """
    WITH
    cte_1 AS (
        SELECT 1
    ),
    cte_2 AS (
        SELECT 2
    ),
    cte_3 AS (
        SELECT 3
    ),
    cte_4 AS (
        SELECT 4
    )

    SELECT var_bar
    FROM cte_3
    """
    result = sqlfluff.lint(sql, rules=["L045"])
    assert result == [
        {
            "code": "L045",
            "description": 'Query defines CTE "cte_1" but does not use it.',
            "line_no": 3,
            "line_pos": 5,
        },
        {
            "code": "L045",
            "description": 'Query defines CTE "cte_2" but does not use it.',
            "line_no": 6,
            "line_pos": 5,
        },
        {
            "code": "L045",
            "description": 'Query defines CTE "cte_4" but does not use it.',
            "line_no": 12,
            "line_pos": 5,
        },
    ]
