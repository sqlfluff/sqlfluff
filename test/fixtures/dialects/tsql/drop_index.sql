-- Syntax 1: DROP INDEX with ON clause (currently supported)
DROP INDEX IX_IndexName ON dbo.TableName;

-- Syntax 2: DROP INDEX with dotted notation (now supported)
-- Supports 2-4 part names: [database.][schema.]table.index
DROP INDEX dbo.TableName.IX_IndexName;

-- Additional variations of Syntax 2
-- 2-part name (table.index)
DROP INDEX TableName.IX_IndexName;

-- 3-part name with brackets
DROP INDEX [dbo].[TableName].[IX_IndexName];

-- 2-part name with brackets
DROP INDEX [TableName].[IX_IndexName];

-- 4-part name (database.schema.table.index)
DROP INDEX MyDB.dbo.TableName.IX_IndexName;

-- With IF EXISTS
DROP INDEX IF EXISTS dbo.TableName.IX_IndexName;

DROP INDEX IF EXISTS TableName.IX_IndexName;
