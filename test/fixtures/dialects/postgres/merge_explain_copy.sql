-- MERGE in EXPLAIN, and in COPY with RETURNING (PostgreSQL 17).
-- https://www.postgresql.org/docs/17/sql-explain.html
-- https://www.postgresql.org/docs/17/sql-copy.html

EXPLAIN MERGE INTO t USING s ON t.id = s.id
WHEN MATCHED THEN DELETE;

EXPLAIN (ANALYZE, COSTS OFF) MERGE INTO t USING s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET v = s.v
WHEN NOT MATCHED THEN INSERT (id, v) VALUES (s.id, s.v);

COPY (
    MERGE INTO t USING s ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET v = s.v
    RETURNING merge_action(), t.id
) TO STDOUT;
