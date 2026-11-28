/* Examples from https://duckdb.org/docs/sql/query_syntax/from */

-- select all columns from the table called "table_name" using the FROM-first syntax
FROM table_name SELECT *;
-- select all columns using the FROM-first syntax and omitting the SELECT clause
FROM table_name;
-- use the FROM-first syntax with WHERE clause and aggregation
FROM range(100) AS t (i) SELECT sum(t.i) WHERE t.i % 2 = 0;

-- FROM-first queries with clauses that immediately follow SELECT
FROM t SELECT a, b GROUP BY ALL;
FROM t SELECT a, count(*) AS cnt GROUP BY a HAVING count(*) > 1 ORDER BY cnt DESC NULLS LAST;
FROM t SELECT a, b WHERE c > 1 GROUP BY ALL ORDER BY ALL;
FROM t SELECT a, sum(a) OVER w WINDOW w AS (ORDER BY a);
FROM t SELECT a, row_number() OVER (ORDER BY a) AS rn QUALIFY rn = 1;
FROM t SELECT a LIMIT 10;
FROM t SELECT a OFFSET 5;
FROM t SELECT a FETCH FIRST 5 ROWS ONLY;

-- FROM-first queries with USING SAMPLE before or after SELECT
FROM addresses USING SAMPLE 10% SELECT city, count(*) GROUP BY city ORDER BY city;
FROM addresses SELECT city, count(*) GROUP BY city ORDER BY city USING SAMPLE 10%;

-- FROM-first queries omitting SELECT with ordering/limiting clauses
FROM t ORDER BY a;
FROM t LIMIT 5;
FROM t OFFSET 5;

-- FROM-first queries in CTEs, subqueries, and parenthesized set branches
WITH cte AS (FROM t SELECT a ORDER BY a) FROM cte LIMIT 5;
SELECT * FROM (FROM t SELECT a ORDER BY a LIMIT 5) AS sub;
(FROM t1 ORDER BY 1 LIMIT 5) UNION ALL (FROM t2 ORDER BY 1 LIMIT 5);
