CREATE OR ALTER FUNCTION [dbo].[add] (@add_1 int, @add_2 int) RETURNS integer
AS
BEGIN
	RETURN @add_1 + @add_2
END
