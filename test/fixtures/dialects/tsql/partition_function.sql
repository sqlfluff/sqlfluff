-- Test $PARTITION function (GitHub issue #8915)
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/partition-transact-sql

-- Basic usage in SELECT
SELECT $PARTITION.MyPartFn(col)
FROM t;

-- Used in WHERE clause
SELECT *
FROM t
WHERE $PARTITION.pf(t.col) = 1;

-- With alias
SELECT $PARTITION.MyPartFn(col) AS partition_number
FROM dbo.MyTable;

-- In a more complex expression
SELECT $PARTITION.MyPartFn(col) + 1 AS next_partition
FROM t;

