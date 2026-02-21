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

-- Use EXECUTE with a character string
EXECUTE ('USE AdventureWorks2022; SELECT BusinessEntityID, JobTitle FROM HumanResources.Employee;');

-- Use EXECUTE to pass a single parameter
EXECUTE dbo.uspGetEmployeeManagers 6;

-- The variable can be explicitly named in the execution:
EXECUTE dbo.uspGetEmployeeManagers @EmployeeID = 6;

-- Use EXECUTE to pass a parameter and capture the output
EXECUTE dbo.uspGetEmployeeManagers @EmployeeID, @ManagerID OUTPUT;
GO

-- first statement in a batch or a sqlcmd script, EXECUTE isn't required.
dbo.uspGetEmployeeManagers @EmployeeID = 6;
GO

-- Use multiple parameters
DECLARE @CheckDate AS DATETIME = GETDATE();
EXECUTE dbo.uspGetWhereUsedProductID 819, @CheckDate;

-- Use EXECUTE 'tsql_string' with a variable
DECLARE @schemaname AS sysname;
DECLARE @tablename AS sysname;
EXECUTE ('ALTER INDEX ALL ON ' +
    @schemaname + '.' +
    @tablename + ' REBUILD;');

-- Use EXECUTE with a remote stored procedure
DECLARE @retstat AS INT;
EXECUTE
    @retstat = SQLSERVER1.AdventureWorks2022.dbo.uspGetEmployeeManagers
    @BusinessEntityID = 6;

-- Use EXECUTE with a stored procedure variable
DECLARE @proc_name AS VARCHAR (30) =  'sys.sp_who';
EXECUTE @proc_name;

-- Using the DEFAULT keyword for the first parameter.
EXECUTE dbo.ProcTestDefaults
    @p1 = DEFAULT,
    @p2 = 'D';

-- Using the DEFAULT keyword for the first and third parameters.
EXECUTE dbo.ProcTestDefaults DEFAULT, 'H', DEFAULT;
EXECUTE dbo.ProcTestDefaults DEFAULT, 'I', @p3 = DEFAULT;

-- Use EXECUTE with AT linked_server_name
EXECUTE ('CREATE TABLE AdventureWorks2022.dbo.SalesTbl
(SalesID INT, SalesName VARCHAR(10)); ') AT SeattleSales;
EXECUTE ('SELECT * FROM scott.emp WHERE MGR = ?', 7902) AT ORACLE;

-- Use EXECUTE WITH RECOMPILE
EXECUTE dbo.Proc_Test_Defaults @p2 = 'A' WITH RECOMPILE;

-- Use EXECUTE with a user-defined function
DECLARE @returnstatus AS NVARCHAR (15);
EXECUTE
    @returnstatus = dbo.ufnGetSalesOrderStatusText
    @Status = 2;

-- Use EXECUTE AS USER to switch context to another user
EXECUTE ('CREATE TABLE Sales.SalesTable (SalesID INT, SalesName VARCHAR(10));')
AS USER = 'User1';

-- Use EXECUTE to redefine a single result set
EXECUTE uspGetEmployeeManagers 16 WITH RESULT SETS
((
    [Reporting Level] INT NOT NULL,
    [ID of Employee] INT NOT NULL,
    [Employee First Name] NVARCHAR (50) NOT NULL,
    [Employee Last Name] NVARCHAR (50) NOT NULL,
    [Employee ID of Manager] NVARCHAR (MAX) NOT NULL,
    [Manager First Name] NVARCHAR (50) NOT NULL,
    [Manager Last Name] NVARCHAR (50) NOT NULL
));

-- Use EXECUTE to redefine a two result sets
EXECUTE Production.ProductList '%tire%' WITH RESULT SETS
(
    -- first result set definition starts here
    (ProductID INT,
    [Name] NAME,
    ListPrice MONEY)
    -- comma separates result set definitions
    ,
    -- second result set definition starts here
    ([Name] NAME,
    NumberOfOrders INT)
);

-- Use EXECUTE with AT DATA_SOURCE data_source_name to query a remote SQL Server
EXECUTE ( 'SELECT @@SERVERNAME' ) AT DATA_SOURCE my_sql_server;

EXECUTE ('sp_who2') AS USER = 'dbo' WITH RESULT SETS UNDEFINED;

-- EXEC with schema name inside string literal concatenated with a variable
-- This pattern is commonly seen when using Jinja templates where a schema
-- variable is rendered inside the string
DECLARE @table_name VARCHAR(MAX);
EXEC('SELECT DISTINCT data_version FROM myschema.' + @table_name);

EXEC('SELECT * FROM myschema.' + @table_name + ' WHERE id = 1');
