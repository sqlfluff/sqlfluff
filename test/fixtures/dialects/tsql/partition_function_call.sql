-- $PARTITION returns the partition number a value maps to
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/partition-transact-sql
SELECT $PARTITION.pf_orders(order_date) AS partition_number
FROM dbo.orders;

SELECT
    $PARTITION.pf_orders(order_date) AS partition_number,
    COUNT(*) AS row_count
FROM dbo.orders
GROUP BY $PARTITION.pf_orders(order_date)
ORDER BY partition_number;

SELECT SalesDb.$PARTITION.pf_orders(1) AS partition_number;

SELECT $partition.[pf_orders](order_date)
FROM dbo.orders
WHERE $PARTITION.pf_orders(order_date) = 3;

CREATE PROCEDURE dbo.get_partition_rows
    @partition_number INT
AS
BEGIN
    SELECT order_id
    FROM dbo.orders
    WHERE $PARTITION.pf_orders(order_date) = @partition_number;
END;
