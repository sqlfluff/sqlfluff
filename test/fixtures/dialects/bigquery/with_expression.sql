-- WITH expression: assign variables, then return the last expression.
-- https://github.com/sqlfluff/sqlfluff/issues/8608
-- https://cloud.google.com/bigquery/docs/reference/standard-sql/operators#with_expression

SELECT WITH(a AS '123',               -- a is '123'
            b AS CONCAT(a, '456'),    -- b is '123456'
            c AS '789',               -- c is '789'
            CONCAT(b, c)) AS result;  -- b + c is '123456789'

SELECT WITH(a AS RAND(), a - a);

SELECT WITH(s AS SUM(input), c AS COUNT(input), s/c)
FROM UNNEST([1.0, 2.0, 3.0]) AS input;

WITH my_table AS (
  SELECT 1 AS x, 2 AS y
  UNION ALL
  SELECT 3 AS x, 4 AS y
  UNION ALL
  SELECT 5 AS x, 6 AS y
)
SELECT WITH(a AS SUM(x), b AS COUNT(x), a/b) AS avg_x, AVG(y) AS avg_y
FROM my_table
WHERE x > 1;

-- A WITH expression inside other expressions.
SELECT
    WITH(a AS 1, a) + 1 AS plus_one,
    CONCAT(WITH(a AS 'x', a), 'y') AS concat_arg,
    WITH(a AS WITH(b AS 1, b + 1), a * 2) AS nested,
    WITH(a AS (SELECT 1), a) AS subquery_variable
FROM t
WHERE WITH(a AS x * 2, a) > 10;
