-- https://github.com/sqlfluff/sqlfluff/issues/3484
WITH cte AS (
    SELECT *
    FROM source
    WHERE col1 = 0
    DISTRIBUTE BY col1
),

SELECT *
FROM cte
