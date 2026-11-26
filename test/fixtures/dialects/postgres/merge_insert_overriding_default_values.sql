-- Merge inserting a row of default values
MERGE INTO t USING s ON t.id = s.id
WHEN NOT MATCHED THEN INSERT DEFAULT VALUES;

-- Merge inserting into an identity column with OVERRIDING SYSTEM VALUE
MERGE INTO t USING s ON t.id = s.id
WHEN NOT MATCHED THEN INSERT (id, val) OVERRIDING SYSTEM VALUE VALUES (s.id, s.val);

-- Merge with OVERRIDING USER VALUE, guarded by an AND condition
MERGE INTO t USING s ON t.id = s.id
WHEN NOT MATCHED AND s.val IS NOT NULL THEN
    INSERT (id, val) OVERRIDING USER VALUE VALUES (s.id, s.val);

-- Merge with OVERRIDING and no column list, alongside the other actions
MERGE INTO t USING s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET val = s.val
WHEN NOT MATCHED THEN INSERT OVERRIDING SYSTEM VALUE VALUES (s.id, s.val);
