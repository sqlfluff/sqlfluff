-- Case and Extract Expressions
-- https://github.com/sqlfluff/sqlfluff/issues/143
SELECT
    CAST(25.65 AS int),
    SAFE_CAST(NULL AS STRING) AS age_label,
    EXTRACT(day FROM end_time) AS day
FROM
    benchmark_with_performance
