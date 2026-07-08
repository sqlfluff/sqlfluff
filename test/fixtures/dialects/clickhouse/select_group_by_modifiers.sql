-- ClickHouse GROUP BY modifiers: WITH ROLLUP / WITH CUBE / WITH TOTALS.
-- https://clickhouse.com/docs/en/sql-reference/statements/select/group-by

SELECT a, count() FROM t GROUP BY a WITH TOTALS;

SELECT a, count() FROM t GROUP BY a WITH ROLLUP;

SELECT a, count() FROM t GROUP BY a WITH CUBE;

SELECT a, b, count() FROM t GROUP BY a, b WITH ROLLUP WITH TOTALS;

SELECT a, b, count() FROM t GROUP BY a, b WITH CUBE WITH TOTALS;
