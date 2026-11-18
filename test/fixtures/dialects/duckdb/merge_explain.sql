-- MERGE INTO in EXPLAIN.
-- https://duckdb.org/docs/stable/guides/meta/explain

EXPLAIN MERGE INTO t USING s ON t.id = s.id
WHEN MATCHED THEN DELETE;

EXPLAIN ANALYZE MERGE INTO t USING s ON t.id = s.id
WHEN NOT MATCHED THEN INSERT VALUES (s.id, s.v);
