SELECT REPLICATE('0', 3 - DATALENGTH(c1)) + c1 AS 'Varchar Column',
       REPLICATE('0', 3 - DATALENGTH(c2)) + c2 AS 'Char Column'
FROM t1;

DECLARE @BinVar varbinary(128);
SET @BinVar = CAST(REPLICATE(0x20, 128) AS varbinary(128) );
