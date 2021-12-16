-- Union All in a With
-- https://github.com/sqlfluff/sqlfluff/issues/162
WITH result AS (
    SELECT
        customer
    FROM sales_eu AS s
    UNION ALL
    SELECT
        customer
    FROM sales_us AS s2
)

SELECT * FROM result
