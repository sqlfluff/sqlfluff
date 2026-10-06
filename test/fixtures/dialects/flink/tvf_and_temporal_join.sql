-- Test Table Valued Functions (TVF) with DESCRIPTOR and TABLE arguments
SELECT *
FROM TABLE(
    TUMBLE(
        TABLE my_table,
        DESCRIPTOR(row_time),
        INTERVAL '10' MINUTES
    )
);

-- Test Temporal Join (Lookup Join)
SELECT
    o.order_id,
    o.total,
    p.product_name
FROM orders AS o
JOIN products FOR SYSTEM_TIME AS OF o.proc_time AS p
    ON o.product_id = p.product_id;
