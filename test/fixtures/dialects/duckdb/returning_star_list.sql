-- `*` can be one item of a RETURNING list, next to other expressions.
-- https://duckdb.org/docs/stable/sql/statements/insert#returning-clause
-- https://duckdb.org/docs/stable/sql/statements/merge_into

INSERT INTO t (id, v) VALUES (5, 'x') RETURNING *, id + 1 AS next_id;

UPDATE t SET v = 'y' WHERE id = 1 RETURNING id, *;

DELETE FROM t WHERE id = 3 RETURNING *, current_date;

MERGE INTO t USING s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET v = s.v
RETURNING merge_action, *;

MERGE INTO t USING s ON t.id = s.id
WHEN NOT MATCHED THEN INSERT (id, v) VALUES (s.id, s.v)
RETURNING *, merge_action AS action;
