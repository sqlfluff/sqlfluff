-- PostgreSQL 17 added `WHEN NOT MATCHED BY SOURCE` and the optional
-- `BY TARGET` qualifier on `WHEN NOT MATCHED`.
-- https://www.postgresql.org/docs/17/sql-merge.html

-- Example adapted from the PostgreSQL 17 MERGE documentation.
MERGE INTO wines w
USING wine_stock_changes s
ON s.winename = w.winename
WHEN NOT MATCHED BY TARGET AND s.stock_delta > 0 THEN
    INSERT VALUES(s.winename, s.stock_delta)
WHEN MATCHED AND w.stock + s.stock_delta > 0 THEN
    UPDATE SET stock = w.stock + s.stock_delta
WHEN NOT MATCHED BY SOURCE THEN
    DELETE;

-- `NOT MATCHED BY SOURCE` combined with `UPDATE` and an extra condition.
MERGE INTO target_table t
USING source_table s
ON t.id = s.id
WHEN MATCHED THEN
    UPDATE SET val = s.val
WHEN NOT MATCHED BY SOURCE AND t.active THEN
    UPDATE SET active = FALSE;

-- `BY TARGET` is an accepted synonym for the plain `WHEN NOT MATCHED`.
MERGE INTO t
USING s
ON t.id = s.id
WHEN NOT MATCHED BY TARGET THEN
    INSERT (id, val) VALUES (s.id, s.val)
WHEN NOT MATCHED BY SOURCE THEN
    DELETE;

-- `NOT MATCHED BY SOURCE` also accepts `DO NOTHING`.
MERGE INTO t
USING s
ON t.id = s.id
WHEN NOT MATCHED BY SOURCE THEN
    DO NOTHING;
