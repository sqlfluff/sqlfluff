-- ClickHouse allows ORDER BY / LIMIT / SETTINGS on a non-final member of an
-- unparenthesised UNION (https://clickhouse.com/docs/en/sql-reference/statements/select/union).

SELECT a FROM t ORDER BY a UNION ALL SELECT b FROM u;

SELECT a FROM t LIMIT 10 UNION ALL SELECT b FROM u;

SELECT a FROM t ORDER BY a LIMIT 10 UNION ALL SELECT b FROM u;

SELECT a FROM t SETTINGS max_threads = 1 UNION ALL SELECT b FROM u;

SELECT a FROM t ORDER BY a
UNION ALL
SELECT b FROM u ORDER BY b
UNION ALL
SELECT c FROM v;
