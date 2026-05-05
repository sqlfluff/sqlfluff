-- Per Microsoft's identifier rules, T-SQL identifier (and parameter) names
-- may contain any Unicode 3.2 letter, not just ASCII A-Z.
-- https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers

-- Cyrillic
DECLARE @Дата DATETIME2 = GETDATE();

-- CJK
DECLARE @正常 INT = 0;

-- Accented Latin (German umlaut + sharp s)
DECLARE @Größe NVARCHAR(50);

-- Greek
DECLARE @Παράμετρος INT;

-- Mixed Unicode + ASCII
DECLARE @user_Имя NVARCHAR(100);

-- Used in SELECT and as procedure parameters
SELECT
    @Дата AS [report_date],
    @正常 AS [status],
    @Größe AS [size];

CREATE PROCEDURE dbo.GetByCriteria
    @Дата DATETIME2,
    @user NVARCHAR(50)
AS
BEGIN
    SELECT @Дата, @user;
END;
