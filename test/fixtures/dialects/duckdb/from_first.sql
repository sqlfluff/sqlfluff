/* Examples from https://duckdb.org/docs/sql/query_syntax/from */

-- select all columns from the table called "table_name" using the FROM-first syntax
FROM table_name SELECT *;
-- select all columns using the FROM-first syntax and omitting the SELECT clause
FROM table_name;
-- use the FROM-first syntax with WHERE clause and aggregation
FROM range(100) AS t (i) SELECT sum(t.i) WHERE t.i % 2 = 0;
