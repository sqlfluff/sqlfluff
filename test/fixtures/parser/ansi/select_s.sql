-- Casting expressions
-- https://github.com/alanmcruickshank/sqlfluff/issues/161
SELECT
    CAST(ROUND(online_sales / 1000.0) AS varchar) AS result
FROM sales