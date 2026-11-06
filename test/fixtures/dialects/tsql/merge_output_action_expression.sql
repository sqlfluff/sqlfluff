-- Issue #8739: T-SQL: $action inside an expression in a MERGE OUTPUT clause
MERGE TargetTable AS T
USING SourceTable AS S
ON (T.ID = S.ID)
WHEN MATCHED THEN
    UPDATE SET T.Val = S.Val
OUTPUT CASE $action WHEN 'INSERT' THEN 'Added' WHEN 'UPDATE' THEN 'Changed' END AS ActionTaken;
GO

MERGE TargetTable AS T
USING SourceTable AS S
ON (T.ID = S.ID)
WHEN MATCHED THEN
    UPDATE SET T.Val = S.Val
OUTPUT IIF($action = 'INSERT', 1, 0) AS IsInsert;
GO

MERGE TargetTable AS T
USING SourceTable AS S
ON (T.ID = S.ID)
WHEN MATCHED THEN
    UPDATE SET T.Val = S.Val
OUTPUT CASE WHEN $action = 'DELETE' THEN 'Deleted' ELSE 'Kept' END AS ActionDesc;
GO

MERGE TargetTable AS T
USING SourceTable AS S
ON (T.ID = S.ID)
WHEN MATCHED AND T.Qty <= 0 THEN
    DELETE
WHEN MATCHED THEN
    UPDATE SET T.Qty = T.Qty - S.Qty
WHEN NOT MATCHED THEN
    INSERT (ID, Qty) VALUES (S.ID, S.Qty)
OUTPUT
    $action AS ActionRaw,
    CASE $action
        WHEN 'INSERT' THEN 'Added'
        WHEN 'UPDATE' THEN 'Changed'
        WHEN 'DELETE' THEN 'Removed'
    END AS ActionTaken,
    IIF($action = 'INSERT', 1, 0) AS IsInsert,
    INSERTED.ID,
    DELETED.ID;
GO
