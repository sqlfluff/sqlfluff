-- `*` can be one item of a RETURNING list, next to other output expressions.
-- https://www.postgresql.org/docs/17/sql-insert.html
-- https://www.postgresql.org/docs/17/sql-merge.html

INSERT INTO t (id, v) VALUES (5, 'x') RETURNING *, id + 1 AS next_id;

UPDATE t SET v = 'y' WHERE id = 1 RETURNING id, *;

DELETE FROM t WHERE id = 3 RETURNING *, now();

MERGE INTO t USING s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET v = s.v
RETURNING merge_action(), *;

MERGE INTO t USING s ON t.id = s.id
WHEN NOT MATCHED THEN INSERT (id, v) VALUES (s.id, s.v)
RETURNING *, merge_action() AS action;

-- PostgreSQL 18 aliases for the old and new rows.
UPDATE t SET v = 'y' WHERE id = 1
RETURNING WITH (OLD AS o) o.v AS old_v, *;
