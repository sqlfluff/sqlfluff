CREATE FUNCTION dbo.ISOweek (@DATE datetime)
RETURNS int
WITH EXECUTE AS CALLER
AS
BEGIN
    DECLARE @ISOweek int;
    SET @ISOweek= DATEPART(wk,@DATE)+1
        -DATEPART(wk,CAST(DATEPART(yy,@DATE) as CHAR(4))+'0104');
--Special cases: Jan 1-3 may belong to the previous year
    IF (@ISOweek=0)
        SET @ISOweek=dbo.ISOweek(CAST(DATEPART(yy,@DATE)-1
            AS CHAR(4))+'12'+ CAST(24+DATEPART(DAY,@DATE) AS CHAR(2)))+1;
--Special case: Dec 29-31 may belong to the next year
    IF ((DATEPART(mm,@DATE)=12) AND
        ((DATEPART(dd,@DATE)-DATEPART(dw,@DATE))>= 28))
    SET @ISOweek=1;
    RETURN(@ISOweek);
END;
GO

CREATE FUNCTION f ()
RETURNS @t TABLE (i int)
AS
BEGIN
    INSERT INTO @t SELECT 1;
    RETURN;
END;
GO

CREATE OR ALTER FUNCTION F (@DATE as datetime) RETURNS INT AS BEGIN RETURN 1 END;
GO

ALTER FUNCTION F (@DATE as datetime) RETURNS INT AS BEGIN RETURN 0 END;
GO

CREATE   FUNCTION [UTIL].[getItemList] (
     @list ItemList READONLY
)
RETURNS nvarchar(max)
AS

BEGIN
      DECLARE @str nvarchar(max) = ''

      SELECT @str = @str + [item] FROM (
        SELECT TOP (9999) [item]
        FROM @list
        ORDER BY [order]
      ) i

      RETURN @str
END;
GO


create function my_function(@my_parameter int)
returns int
with schemabinding, returns null on null input
begin
    return @my_parameter
end
go
