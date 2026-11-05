-- A WITH clause before MERGE, and MERGE as a data-modifying statement inside
-- a WITH clause (the latter needs RETURNING, added in PostgreSQL 17).
-- https://www.postgresql.org/docs/17/sql-merge.html
-- https://www.postgresql.org/docs/17/queries-with.html#QUERIES-WITH-MODIFYING

WITH src AS (
    SELECT id, v FROM s WHERE id > 0
)
MERGE INTO t USING src ON t.id = src.id
WHEN MATCHED THEN UPDATE SET v = src.v
WHEN NOT MATCHED THEN INSERT (id, v) VALUES (src.id, src.v);

WITH a AS (SELECT id, v FROM s), b AS (SELECT id, v FROM a WHERE id > 1)
MERGE INTO t USING b ON t.id = b.id
WHEN NOT MATCHED THEN DO NOTHING;

WITH src AS MATERIALIZED (SELECT id FROM s)
MERGE INTO t AS tgt USING src ON tgt.id = src.id
WHEN MATCHED THEN DELETE;

WITH src AS (SELECT id, v FROM s)
MERGE INTO t USING src ON t.id = src.id
WHEN MATCHED THEN UPDATE SET v = src.v
RETURNING merge_action(), t.*;

WITH merged AS (
    MERGE INTO t USING s ON t.id = s.id
    WHEN MATCHED THEN UPDATE SET v = s.v
    WHEN NOT MATCHED THEN INSERT (id, v) VALUES (s.id, s.v)
    RETURNING merge_action() AS action, t.id
)
SELECT action, count(*) FROM merged GROUP BY action;
