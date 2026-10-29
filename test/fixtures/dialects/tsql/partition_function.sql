-- https://learn.microsoft.com/en-us/sql/t-sql/functions/partition-transact-sql

SELECT
    $PARTITION.TransactionRangePF1(TransactionDate) AS Partition,
    COUNT(Ra.TransactionID) AS Records
FROM Production.TransactionHistoryRa
GROUP BY $PARTITION.TransactionRangePF1(TransactionDate)
ORDER BY Partition;

SELECT
    Ra.TransactionDate,
    Ra.TransactionID
FROM Production.TransactionHistoryRa
WHERE $PARTITION.TransactionRangePF1(TransactionDate) = 5;

SELECT my_database.$PARTITION.my_pf(id) FROM dbo.test_partitions;

CREATE PROCEDURE [dbo].[get_test_partitions_at_partition]
    @partition_number INT
AS
BEGIN
    SELECT
        id,
        shenanigans
    FROM dbo.test_partitions
    WHERE $PARTITION.pf_test(id) = @partition_number
END
GO
