-- including just in case; Azure Synapse Analytics does not support OR ALTER
-- https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-sql-data-warehouse?view=aps-pdw-2016-au7
CREATE FUNCTION [dbo].[add] (@add_1 int, @add_2 int) RETURNS integer
AS
BEGIN
	RETURN @add_1 + @add_2
END
