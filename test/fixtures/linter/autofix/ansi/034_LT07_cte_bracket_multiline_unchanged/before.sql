WITH cte AS (
    SELECT
        a,
        b
    FROM foo
)

SELECT
    a,
    b
FROM cte
