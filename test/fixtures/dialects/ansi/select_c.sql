-- Thanks @mrshu for this query, it tests functions and order by
SELECT
    col_a,
    col_b,
    date_col_a,
    date_col_b
FROM "database"."sample_table"
WHERE
    DATE(date_col_b) >= current_date
    AND length(col_a) = 4
ORDER BY date_col_a DESC NULLS LAST
