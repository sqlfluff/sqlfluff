-- Testing $PARTITION system function and other dollar identifiers in T-SQL
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/partition-transact-sql

SELECT $PARTITION.myRangePF1(c1) FROM dbo.t1;

SELECT c1, $PARTITION.pf1(c2) AS part_num
FROM dbo.t1
WHERE $PARTITION.pf1(c2) = 2;

CREATE PROCEDURE [dbo].[get_test_partitions_at_partition]
AS
BEGIN
    SELECT $PARTITION.pf_test(col1) AS partition_num
    FROM [dbo].[test_table];
END;

SELECT $IDENTITY FROM dbo.t1;

SELECT $ROWGUID FROM dbo.t1;

SELECT $node_id, name FROM dbo.Person;
