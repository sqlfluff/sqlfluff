"""Tests observed conflict between ST05 & LT09."""

from sqlfluff.core import FluffConfig, Linter


def test__rules__std_ST05_LT08_5265() -> None:
    """Tests observed conflict between ST05 & LT09.

    In this case, the moved `t2` table was created after the first usage.
    https://github.com/sqlfluff/sqlfluff/issues/4137
    """
    sql = """
WITH
cte1 AS (
    SELECT COUNT(*) AS qty
    FROM some_table AS st
    LEFT JOIN (
        SELECT 'first' AS id
    ) AS oops
    ON st.id = oops.id
),
cte2 AS (
    SELECT COUNT(*) AS other_qty
    FROM other_table AS sot
    LEFT JOIN (
        SELECT 'middle' AS id
    ) AS another
    ON sot.id = another.id
    LEFT JOIN (
        SELECT 'last' AS id
    ) AS oops
    ON sot.id = oops.id
)
SELECT CURRENT_DATE();
"""
    fixed_sql = """
WITH oops AS (
        SELECT 'first' AS id
    ),

cte1 AS (
    SELECT COUNT(*) AS qty
    FROM some_table AS st
    LEFT JOIN oops
    ON st.id = oops.id
),

another AS (
        SELECT 'middle' AS id
    ),

cte2 AS (
    SELECT COUNT(*) AS other_qty
    FROM other_table AS sot
    LEFT JOIN another
    ON sot.id = another.id
    LEFT JOIN (
        SELECT 'last' AS id
    ) AS oops
    ON sot.id = oops.id
)

SELECT CURRENT_DATE();
"""
    cfg = FluffConfig.from_kwargs(
        dialect="ansi",
        rules=["ST05", "LT08"],
    )
    result = Linter(config=cfg).lint_string(sql, fix=True)
    assert result.fix_string()[0] == fixed_sql
