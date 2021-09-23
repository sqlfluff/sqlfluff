--https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-sql-data-warehouse?view=azure-sqldw-latest
CREATE FUNCTION [dbo].[CONVERT_ISO_WEEK_TO_UNIX] (@year INT, @week INT)
RETURNS BIGINT
AS
    BEGIN
        DECLARE @result BIGINT
        SET @result=4
        RETURN @result + @year + @week
    END
