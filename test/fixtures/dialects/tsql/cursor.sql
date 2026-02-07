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
