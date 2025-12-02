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
