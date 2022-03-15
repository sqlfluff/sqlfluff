WITH prep_1 AS (
    SELECT
        *,
        margin
    FROM b_table
)
SELECT *
FROM a_table
INNER JOIN prep_1 ON a_table.some_column = prep_1.some_column
