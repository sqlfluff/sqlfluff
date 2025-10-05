-- Print the value of a variable initialized by using SET
DECLARE @myVar CHAR(20);
SET @myVar = 'This is a test';
SELECT @myVar;
GO

-- Use a local variable assigned a value by using SET in a SELECT statement
DECLARE @state CHAR(25);
SET @state = N'Oregon';
SELECT
    CITY,
    RTRIM(FIRSTNAME) + ' ' + RTRIM(LASTNAME) AS FULL_NAME
FROM HUMANRESOURCES.VEMPLOYEE
WHERE STATEPROVINCENAME = @state;

-- Use a compound assignment for a local variable
DECLARE @NewBalance INT;
SET @NewBalance = 10;
SET @NewBalance = @NewBalance * 10;
SELECT @NewBalance;
GO

-- Use SET with a global cursor
DECLARE MY_CURSOR CURSOR GLOBAL
FOR SELECT SHIP_DATE FROM PURCHASING.SHIPMETHOD
DECLARE @my_variable CURSOR;
SET @my_variable = MY_CURSOR;

DEALLOCATE MY_CURSOR;
GO

-- Define a cursor by using SET
DECLARE @CursorVar CURSOR;

SET
    @CursorVar = CURSOR SCROLL DYNAMIC
    FOR
    SELECT
        LASTNAME,
        FIRSTNAME
    FROM ADVENTUREWORKS2022.HUMANRESOURCES.EMPLOYEE
    WHERE LASTNAME LIKE 'B%';

OPEN @CursorVar;

FETCH NEXT FROM @CursorVar;
WHILE @@FETCH_STATUS = 0
    BEGIN
        FETCH NEXT FROM @CursorVar
    END;

CLOSE @CursorVar;
DEALLOCATE @CursorVar;
GO

-- Assign a value from a query
USE ADVENTUREWORKS2022;
GO
DECLARE @rows INT;
SET @rows = (SELECT COUNT(*) FROM SALES.CUSTOMER);
SELECT @rows;
GO

-- Single params
SET @param1 = 1
;

-- Multiple params
SET
    @param1 = 1,
    @param2 = 2
;

-- Comma separated params with comment with comma
SET @param1 = "test, test",
    @param2 = 2
;

-- Params with expression
SET @param1 = ("test", "test"),
    @param2 = 2
;

-- Assignment operators
SET @param1 += 1,
    @param2 -= 2,
    @param3 *= 3,
    @param4 /= 4,
    @param5 %= 5,
    @param5 ^= 6,
    @param5 &= 7,
    @param5 |= 8
;

-- Param with sequence in expression
SET @param1 = (NEXT VALUE FOR [dbo].[sequence_name])
;
