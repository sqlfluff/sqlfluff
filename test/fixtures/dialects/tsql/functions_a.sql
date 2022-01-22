SELECT
    DATE(t) AS t_date,
    ROUND(b, 2) AS b_round,
    LEFT(RIGHT(s, 5), LEN(s + 6)) AS compound,
    DATEADD(month, -1, column1) AS column1_lastmonth,
    convert(varchar, tbl_b.column1, 23) AS column1_varchar
FROM tbl_b
GO

CREATE FUNCTION dbo.RandDate
(
@admit       DATE
)
RETURNS TABLE
AS
     RETURN
(
    SELECT @admit 
    FROM   dbo.[RandomDate]
);
GO
