-- DuckDB sampling. https://duckdb.org/docs/stable/sql/samples
--
-- `USING SAMPLE` is a query-level clause: it samples the result of the whole
-- FROM clause (after joins), so it trails the query. `TABLESAMPLE` is the
-- table-level form: it samples an individual table (before joins).

-- Percentage samples.
SELECT * FROM addresses USING SAMPLE 10%;
SELECT * FROM addresses USING SAMPLE 10 PERCENT;

-- Fixed row-count samples (a bare number, or `ROWS`). Only reservoir sampling
-- supports a fixed number of rows.
SELECT * FROM addresses USING SAMPLE 5;
SELECT * FROM addresses USING SAMPLE 100 ROWS;

-- A sampling method applied to a size. `reservoir` accepts a percentage or a
-- row count; `bernoulli` and `system` are percentage-only.
SELECT * FROM addresses USING SAMPLE reservoir(20%);
SELECT * FROM addresses USING SAMPLE reservoir(500 ROWS);
SELECT * FROM addresses USING SAMPLE bernoulli(10%);
SELECT * FROM addresses USING SAMPLE system(20%);
SELECT * FROM addresses USING SAMPLE reservoir(50 ROWS) REPEATABLE (100);

-- A percentage with an explicit method (and optional seed) -- any method.
SELECT * FROM addresses USING SAMPLE 10 PERCENT (bernoulli);
SELECT * FROM addresses USING SAMPLE 20% (system, 377);

-- A fixed row count with an explicit method (and optional seed) -- reservoir only.
SELECT * FROM addresses USING SAMPLE 10 ROWS (reservoir, 354);

-- `USING SAMPLE` samples after joins, so it trails the whole query.
SELECT *
FROM tbl, tbl2
WHERE tbl.i = tbl2.i
USING SAMPLE reservoir(20%);

SELECT city, count(*)
FROM addresses
GROUP BY city
ORDER BY city
USING SAMPLE 10%;

-- `TABLESAMPLE` samples before joins, so it attaches to a table in FROM.
SELECT * FROM addresses TABLESAMPLE 10%;
SELECT * FROM addresses TABLESAMPLE bernoulli(10%);
SELECT *
FROM tbl TABLESAMPLE reservoir(20%), tbl2
WHERE tbl.i = tbl2.i;

-- `USING SAMPLE` also trails a `SELECT` that is a branch of a set expression,
-- so it can sample either (or both) sides of a `UNION`.
SELECT * FROM tbl USING SAMPLE 10%
UNION ALL
SELECT * FROM other;

SELECT * FROM tbl
UNION ALL
SELECT * FROM other USING SAMPLE 10%;

SELECT * FROM a USING SAMPLE 5 ROWS
UNION
SELECT * FROM b USING SAMPLE 10%
ORDER BY 1;
