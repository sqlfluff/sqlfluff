-- https://clickhouse.com/docs/sql-reference/statements/select/with
-- Materialized CTEs (ClickHouse 26.3+)

WITH a AS MATERIALIZED (SELECT 1 AS x)
SELECT * FROM a;

WITH cte (x) AS MATERIALIZED (SELECT 1)
SELECT x FROM cte;

WITH
    a AS MATERIALIZED (SELECT 1 AS uid, 'Alice' AS name)
SELECT count()
FROM a AS l
JOIN a AS r ON l.uid = r.uid;
