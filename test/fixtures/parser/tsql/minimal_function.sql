CREATE OR ALTER FUNCTION [dbo].[add] (@add_1 int, @add_2 int) RETURNS integer
AS 
BEGIN
	DECLARE @time int = 1
	SELECT * FROM Table
	RETURN @add_1 + @add_2
END
	
