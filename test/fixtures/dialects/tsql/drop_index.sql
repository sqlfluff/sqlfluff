-- Traditional syntax with ON clause
DROP INDEX IX_IndexName ON dbo.TableName;

-- Dotted notation
DROP INDEX dbo.TableName.IX_IndexName;

DROP INDEX TableName.IX_IndexName;

DROP INDEX [dbo].[TableName].[IX_IndexName];

DROP INDEX [TableName].[IX_IndexName];

DROP INDEX MyDB.dbo.TableName.IX_IndexName;

-- With IF EXISTS
DROP INDEX IF EXISTS dbo.TableName.IX_IndexName;

DROP INDEX IF EXISTS TableName.IX_IndexName;
