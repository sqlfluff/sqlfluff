SELECT
    col_a,
    col_b
FROM some_table
WHERE col_a IS NOT NULL
AND col_b NOT IN (SELECT c FROM another_table)
