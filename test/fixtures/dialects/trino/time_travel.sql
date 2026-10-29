-- https://trino.io/docs/current/connector/iceberg.html#time-travel-queries
SELECT * FROM example.testdb.customer_orders FOR VERSION AS OF 8954597067493422955;

SELECT * FROM example.testdb.customer_orders FOR VERSION AS OF 'historical-tag';

SELECT * FROM example.testdb.customer_orders
FOR TIMESTAMP AS OF TIMESTAMP '2022-03-23 09:59:29.803 Europe/Vienna';

SELECT * FROM orders FOR TIMESTAMP AS OF current_timestamp - INTERVAL '1' DAY AS old_orders;

SELECT o.id, c.name
FROM orders FOR VERSION AS OF 3 AS o
JOIN customers c ON o.customer_id = c.id;

-- A plain alias named "for" style words still works without time travel
SELECT version FROM orders;
