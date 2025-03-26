EXEC [Reporting].[Load_CLL]

-- Specifying a value only for one parameter (@p2).
EXECUTE dbo.ProcTestDefaults @p2 = 'A';
-- Specifying a value for the first two parameters.
EXECUTE dbo.ProcTestDefaults 68, 'B';
-- Specifying a value for all three parameters.
EXECUTE dbo.ProcTestDefaults 68, 'C', 'House';
-- Using the DEFAULT keyword for the first parameter.
EXECUTE dbo.ProcTestDefaults @p1 = DEFAULT, @p2 = 'D';
-- Specifying the parameters in an order different from the order defined in the procedure.
EXECUTE dbo.ProcTestDefaults DEFAULT, @p3 = 'Local', @p2 = 'E';
-- Using the DEFAULT keyword for the first and third parameters.
EXECUTE dbo.ProcTestDefaults DEFAULT, 'H', DEFAULT;
EXECUTE dbo.ProcTestDefaults DEFAULT, 'I', @p3 = DEFAULT;


EXECUTE sp_addextendedproperty
@name = N'MS_Description',
@value = 'my text description',
@level0type = N'SCHEMA',
@level0name = N'my_schema_name',
@level1type = N'my_object_type',
@level1name = N'my_object_name'


-- Executing a stored procedure and capturing the RETURN value in a variable
EXEC @pRes = dbo.ProcTestDefaults;
EXEC @pRes = dbo.ProcTestDefaults @p1 = DEFAULT;
EXECUTE @pRes = dbo.ProcTestDefaults;
EXECUTE @pRes = dbo.ProcTestDefaults @p1 = DEFAULT;

-- Executing statement from a variable
DECLARE @statement nvarchar(max) = 'SELECT 1'
EXEC (@statement);

EXEC ('DROP TABLE BoardInventory.BoardInventoryFact_Stage;');

DECLARE @s1 AS varchar(10) = NULL;
DECLARE @s2 varchar(10) = NULL;
SET @s1 = 'select ';
SET @s2 = '123';
EXECUTE (@s1 + @s2);

EXEC ('select ' + '123');
