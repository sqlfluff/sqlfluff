-- Mixing ordinary grouping expressions with GROUPING SETS / ROLLUP / CUBE
-- https://docs.snowflake.com/en/sql-reference/constructs/group-by
SELECT a, b, count(*)
FROM t
GROUP BY a, GROUPING SETS (b, ());

SELECT a, b, c, sum(x)
FROM t
GROUP BY a, ROLLUP (b, c), CUBE (b);

SELECT a, b, sum(x)
FROM t
GROUP BY GROUPING SETS (a, ROLLUP (b), ());

SELECT a, sum(x)
FROM t
GROUP BY 1, coalesce(a, 'x');
