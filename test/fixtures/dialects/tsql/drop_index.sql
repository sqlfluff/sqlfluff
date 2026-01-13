DROP INDEX IX_IndexName ON dbo.TableName;

DROP INDEX IF EXISTS IX_IndexName ON dbo.TableName;

DROP INDEX IX_IndexName ON MyDB.dbo.TableName;

DROP INDEX IF EXISTS IX_IndexName ON MyDB.dbo.TableName;

DROP INDEX dbo.TableName.IX_IndexName;

DROP INDEX TableName.IX_IndexName;

DROP INDEX [dbo].[TableName].[IX_IndexName];

DROP INDEX [TableName].[IX_IndexName];

DROP INDEX IF EXISTS dbo.TableName.IX_IndexName;

DROP INDEX IF EXISTS TableName.IX_IndexName;
