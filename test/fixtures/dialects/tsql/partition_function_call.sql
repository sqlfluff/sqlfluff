SELECT $PARTITION.pf_orders(order_date) FROM dbo.orders;

SELECT $PARTITION.pf_orders(order_date) AS partition_number, COUNT(*) AS row_count
FROM dbo.orders
GROUP BY $PARTITION.pf_orders(order_date);

SELECT * FROM dbo.orders WHERE $PARTITION.pf_orders(order_date) = 2;

SELECT testdb.$PARTITION.[pf_orders](order_date) FROM dbo.orders;

SELECT $partition.pf_orders(order_date) FROM dbo.orders;

CREATE PROCEDURE [dbo].[get_partitions]
AS
BEGIN
    SELECT $PARTITION.pf_orders(order_date) AS partition_number
    FROM dbo.orders;
END;
