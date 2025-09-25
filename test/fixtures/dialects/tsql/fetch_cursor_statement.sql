-- Using FETCH in a simple cursor
USE ADVENTUREWORKS2022;
GO
DECLARE CONTACT_CURSOR CURSOR FOR
SELECT LASTNAME FROM PERSON.PERSON
WHERE LASTNAME LIKE 'B%'
ORDER BY LASTNAME;

OPEN CONTACT_CURSOR;

-- Perform the first fetch.
FETCH NEXT FROM CONTACT_CURSOR;

-- Check @@FETCH_STATUS to see if there are any more rows to fetch.
WHILE @@FETCH_STATUS = 0
    BEGIN
        -- This is executed as long as the previous fetch succeeds.
        FETCH NEXT FROM CONTACT_CURSOR;
    END

CLOSE CONTACT_CURSOR;
DEALLOCATE CONTACT_CURSOR;
GO

-- Using FETCH to store values in variables
USE ADVENTUREWORKS2022;
GO
-- Declare the variables to store the values returned by FETCH.
DECLARE @LastName VARCHAR(50), @FirstName VARCHAR(50);

DECLARE CONTACT_CURSOR CURSOR FOR
SELECT
    LASTNAME,
    FIRSTNAME
FROM PERSON.PERSON
WHERE LASTNAME LIKE 'B%'
ORDER BY LASTNAME, FIRSTNAME;

OPEN CONTACT_CURSOR;

-- Perform the first fetch and store the values in variables.
-- Note: The variables are in the same order as the columns
-- in the SELECT statement.

FETCH NEXT FROM CONTACT_CURSOR
INTO @LastName, @FirstName;

-- Check @@FETCH_STATUS to see if there are any more rows to fetch.
WHILE @@FETCH_STATUS = 0
    BEGIN

        -- Concatenate and display the current values in the variables.
        PRINT 'Contact Name: ' + @FirstName + ' ' + @LastName

        -- This is executed as long as the previous fetch succeeds.
        FETCH NEXT FROM CONTACT_CURSOR
        INTO @LastName, @FirstName;
    END

CLOSE CONTACT_CURSOR;
DEALLOCATE CONTACT_CURSOR;
GO

-- Declaring a SCROLL cursor and using the other FETCH options
USE ADVENTUREWORKS2022;
GO
-- Execute the SELECT statement alone to show the
-- full result set that is used by the cursor.
SELECT
    LASTNAME,
    FIRSTNAME
FROM PERSON.PERSON
ORDER BY LASTNAME, FIRSTNAME;

-- Declare the cursor.
DECLARE @contact_cursor SCROLL CURSOR FOR
SELECT [LastName], [FirstName] FROM [Person].[Person]
ORDER BY [LastName], [FirstName];

OPEN contact_cursor;

-- Fetch the last row in the cursor.
FETCH LAST FROM contact_cursor;

-- Fetch the row immediately prior to the current row in the cursor.
FETCH PRIOR FROM contact_cursor;

-- Fetch the second row in the cursor.
FETCH ABSOLUTE 2 FROM contact_cursor;

-- Fetch the row that is three rows after the current row.
FETCH RELATIVE 3 FROM contact_cursor;

-- Fetch the row that is two rows prior to the current row.
FETCH RELATIVE -2 FROM contact_cursor;

CLOSE contact_cursor;
DEALLOCATE contact_cursor;
