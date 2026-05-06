DECLARE pointy CURSOR LOCAL FORWARD_ONLY READ_ONLY FOR
SELECT
    column_a,
    column_b
FROM some_table
WHERE column_a IS NOT NULL
ORDER BY column_b

OPEN pointy;

FETCH FIRST FROM @pointy INTO @result;
FETCH NEXT FROM GLOBAL pointy;

CLOSE GLOBAL pointy;

DEALLOCATE pointy;

DECLARE @cursorName CURSOR;
GO

DECLARE db_cursor CURSOR LOCAL FORWARD_ONLY FAST_FORWARD TYPE_WARNING FOR
SELECT Id, SomeColumn, AnotherColumn FROM dbo.SomeTable FOR UPDATE OF SomeColumn, AnotherColumn;
OPEN db_cursor;
UPDATE dbo.SomeTable SET SomeColumn = 'NewValue' WHERE CURRENT OF db_cursor;
CLOSE db_cursor;
DEALLOCATE db_cursor
GO

-- out of order
DECLARE db_cursor CURSOR TYPE_WARNING FAST_FORWARD LOCAL FORWARD_ONLY FOR
SELECT Id, SomeColumn, AnotherColumn FROM dbo.SomeTable FOR UPDATE OF SomeColumn, AnotherColumn;
OPEN db_cursor;
UPDATE dbo.SomeTable SET SomeColumn = 'NewValue' WHERE CURRENT OF db_cursor;
CLOSE db_cursor;
DEALLOCATE db_cursor
GO

DECLARE db_cursor CURSOR GLOBAL SCROLL KEYSET READ_ONLY FOR
SELECT Id, SomeColumn FROM dbo.SomeTable;
OPEN GLOBAL db_cursor;
CLOSE GLOBAL db_cursor;
DEALLOCATE GLOBAL db_cursor;
GO

DECLARE @db_cursor CURSOR LOCAL FORWARD_ONLY FAST_FORWARD TYPE_WARNING FOR
SELECT Id, SomeColumn, AnotherColumn FROM dbo.SomeTable FOR UPDATE;
OPEN @db_cursor;
DELETE FROM dbo.SomeTable WHERE CURRENT OF db_cursor;
CLOSE @db_cursor;
DEALLOCATE @db_cursor
GO

DECLARE db_cursor INSENSITIVE SCROLL CURSOR FOR
SELECT Id, SomeColumn FROM dbo.SomeTable FOR UPDATE OF SomeColumn;
OPEN db_cursor;
FETCH ABSOLUTE @Rows FROM db_cursor;
GO

DECLARE db_cursor SCROLL INSENSITIVE  CURSOR FOR
SELECT Id, SomeColumn FROM dbo.SomeTable FOR UPDATE OF SomeColumn;
OPEN db_cursor;
FETCH ABSOLUTE @Rows FROM db_cursor;
GO

DECLARE @table AS TABLE (id int, name varchar(128));
DECLARE db_cursor SCROLL INSENSITIVE  CURSOR FOR
SELECT Id, SomeColumn FROM @table FOR UPDATE OF SomeColumn;
OPEN db_cursor;
FETCH ABSOLUTE @Rows FROM db_cursor;
GO

DECLARE cur_union CURSOR LOCAL FAST_FORWARD FOR
SELECT 1 AS Id
UNION ALL
SELECT 2 AS Id;
OPEN cur_union;
CLOSE cur_union;
DEALLOCATE cur_union;
GO

DECLARE cur_union_legacy INSENSITIVE SCROLL CURSOR FOR
SELECT 1 AS Id
UNION ALL
SELECT 2 AS Id;
OPEN cur_union_legacy;
CLOSE cur_union_legacy;
DEALLOCATE cur_union_legacy;
GO

DECLARE cur_cte CURSOR LOCAL FAST_FORWARD FOR
WITH cte AS (
    SELECT 1 AS Id
)
SELECT Id FROM cte;
OPEN cur_cte;
CLOSE cur_cte;
DEALLOCATE cur_cte;
GO
