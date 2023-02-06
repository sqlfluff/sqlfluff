-- Select Query Temporal Tables

SELECT * FROM Employee
  FOR SYSTEM_TIME
    BETWEEN '2021-01-01 00:00:00.0000000' AND '2022-01-01 00:00:00.0000000';

SELECT * FROM Employee
  FOR SYSTEM_TIME ALL;


 SELECT * FROM Employee
  FOR SYSTEM_TIME
    FROM '2021-01-01 00:00:00.0000000' TO '2022-01-01 00:00:00.0000000';

SELECT * FROM Employee
  FOR SYSTEM_TIME
    AS OF '2021-01-01 00:00:00.0000000';

SELECT * FROM Employee
  FOR SYSTEM_TIME
    CONTAINED IN ('2021-01-01 00:00:00.0000000', '2022-01-01 00:00:00.0000000');

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
