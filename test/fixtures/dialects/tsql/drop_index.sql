-- Syntax 1: DROP INDEX with ON clause (currently supported)
DROP INDEX IX_IndexName ON dbo.TableName;

-- Syntax 2: DROP INDEX with dotted notation (NOT currently supported)
-- This is the three-part name format: [schema.]table.index
DROP INDEX dbo.TableName.IX_IndexName;

-- Additional variations of Syntax 2
DROP INDEX TableName.IX_IndexName;

DROP INDEX [dbo].[TableName].[IX_IndexName];

DROP INDEX [TableName].[IX_IndexName];

-- With IF EXISTS (if supported)
DROP INDEX IF EXISTS dbo.TableName.IX_IndexName;

DROP INDEX IF EXISTS TableName.IX_IndexName;
