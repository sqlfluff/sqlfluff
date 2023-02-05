-- Query Temporal Tables
-- SELECT
--     a
--     , b
-- FROM Sales FOR SYSTEM_TIME ALL AS Sales;
-- GO

-- SELECT [DeptID], [DeptName], [ValidFrom], [ValidTo]
-- FROM [dbo].[Department]
-- FOR SYSTEM_TIME AS OF '2021-09-01 T10:00:00.7230011';
-- GO

-- SELECT [DeptID], [DeptName], [ValidFrom], [ValidTo]
-- FROM [dbo].[Department] FOR SYSTEM_TIME AS OF @ADayAgo AS D_1_Ago;
-- GO

-- SELECT
--      [DeptID]
--    , [DeptName]
--    , [ValidFrom]
--    , [ValidTo]
--    , IIF (YEAR(ValidTo) = 9999, 1, 0) AS IsActual
-- FROM [dbo].[Department]
-- FOR SYSTEM_TIME BETWEEN '2021-01-01' AND '2021-12-31'
-- WHERE DeptId = 1
-- ORDER BY ValidFrom DESC;
-- GO

-- SELECT [DeptID], [DeptName], [ValidFrom],[ValidTo]
-- FROM [dbo].[Department]
-- FOR SYSTEM_TIME CONTAINED IN ('2021-04-01', '2021-09-25')
-- WHERE DeptId = 1
-- ORDER BY ValidFrom DESC;
-- GO

-- Create Temporal Tables

CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.EmployeeHistory), DURABILITY = SCHEMA_ONLY );
;
GO

CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (FILETABLE_PRIMARY_KEY_CONSTRAINT_NAME = COLUMNC );
;
GO

CREATE TABLE [dbo].[EC DC] (
    [Column B] [varchar](100),
    [ColumnC] varchar(100),
    [ColumnDecimal] decimal(10,3)
)
WITH (DATA_DELETION = ON (FILTER_COLUMN = ColumnC, RETENTION_PERIOD = INFINITE));
;
GO
