-- Full Join
-- https://github.com/sqlfluff/sqlfluff/issues/144
SELECT
    exists_left.business_type AS business_type_left,
    exists_right.business_type AS business_type_right
FROM
    benchmark_summaries AS exists_left
FULL JOIN
    business_types AS exists_right
ON
    exists_left.business_type = exists_right.business_type
