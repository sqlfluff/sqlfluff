INSERT INTO t1 (a, b) VALUES (1, 2) ON CONFLICT DO NOTHING;

INSERT INTO t1 (a, b) VALUES (1, 2) ON CONFLICT (a, b) DO NOTHING;

INSERT INTO t1 (a, b)
VALUES (1, 2)
ON CONFLICT (a, b) DO UPDATE SET
a = excluded.a;

INSERT INTO t1 (a, b)
VALUES (1, 2)
ON CONFLICT (a, b) DO UPDATE SET
a = excluded.a WHERE a < 10;

INSERT INTO t1 (a, b)
VALUES (1, 2)
ON CONFLICT (a, b) DO UPDATE SET
a = excluded.a WHERE a < 10
RETURNING *;

-- Multiple conflict targets with a conditional update and RETURNING.
INSERT INTO t1 (a, b)
VALUES (1, 2)
ON CONFLICT (a) DO UPDATE SET b = excluded.b WHERE excluded.b < 10
ON CONFLICT (b) DO NOTHING
RETURNING *;

-- INSERT SELECT with a final targetless conflict clause.
INSERT INTO t1 (a, b)
SELECT 1, 2 WHERE true
ON CONFLICT (a) DO NOTHING
ON CONFLICT DO UPDATE SET b = excluded.b
RETURNING a, b;

-- More than two clauses, ending with a catch-all for other unique constraints.
INSERT INTO t1 (a, b, c)
VALUES (1, 2, 3)
ON CONFLICT (a) DO NOTHING
ON CONFLICT (b) DO UPDATE SET c = excluded.c
ON CONFLICT DO NOTHING;
