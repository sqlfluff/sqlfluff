"""Tests the python routines within ST03."""

import sqlfluff


def test__rules__std_ST03_multiple_unused_ctes():
    """Verify that ST03 returns multiple lint issues, one per unused CTE."""
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
    result = sqlfluff.lint(sql, rules=["ST03"])
    assert result == [
        {
            "code": "ST03",
            "description": 'Query defines CTE "cte_1" but does not use it.',
            "name": "structure.unused_cte",
            "warning": False,
            "fixes": [],
            "start_line_no": 3,
            "start_line_pos": 5,
            "start_file_pos": 14,
            "end_line_no": 3,
            "end_line_pos": 10,
            "end_file_pos": 19,
        },
        {
            "code": "ST03",
            "description": 'Query defines CTE "cte_2" but does not use it.',
            "name": "structure.unused_cte",
            "warning": False,
            "fixes": [],
            "start_line_no": 6,
            "start_line_pos": 5,
            "start_file_pos": 53,
            "end_line_no": 6,
            "end_line_pos": 10,
            "end_file_pos": 58,
        },
        {
            "code": "ST03",
            "description": 'Query defines CTE "cte_4" but does not use it.',
            "name": "structure.unused_cte",
            "warning": False,
            "fixes": [],
            "start_line_no": 12,
            "start_line_pos": 5,
            "start_file_pos": 131,
            "end_line_no": 12,
            "end_line_pos": 10,
            "end_file_pos": 136,
        },
    ]
