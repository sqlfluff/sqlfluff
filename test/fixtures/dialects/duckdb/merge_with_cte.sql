-- A WITH clause before MERGE INTO.
-- https://duckdb.org/docs/stable/sql/statements/merge_into

WITH src AS (
    SELECT id, v FROM s WHERE id > 0
)
MERGE INTO t USING src ON t.id = src.id
WHEN MATCHED THEN UPDATE SET v = src.v
WHEN NOT MATCHED THEN INSERT (id, v) VALUES (src.id, src.v);

WITH a AS (SELECT id, v FROM s), b AS (SELECT id, v FROM a WHERE id > 1)
MERGE INTO t USING b ON t.id = b.id
WHEN NOT MATCHED THEN INSERT VALUES (b.id, b.v)
RETURNING merge_action, t.id;

WITH src AS MATERIALIZED (SELECT id FROM s)
MERGE INTO t AS tgt USING src ON tgt.id = src.id
WHEN MATCHED THEN DELETE;
