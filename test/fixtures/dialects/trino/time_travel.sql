SELECT *
FROM example.testdb.customer_orders FOR VERSION AS OF 8954597067493422955;

SELECT *
FROM example.testdb.customer_orders FOR VERSION AS OF 'historical-tag';

SELECT *
FROM example.testdb.customer_orders
FOR TIMESTAMP AS OF TIMESTAMP '2022-03-23 09:59:29.803 Europe/Vienna';

SELECT *
FROM example.testdb.customer_orders FOR TIMESTAMP AS OF DATE '2022-03-23';

SELECT *
FROM customer_orders FOR TIMESTAMP AS OF current_timestamp - INTERVAL '1' DAY;

SELECT o.order_id
FROM customer_orders FOR VERSION AS OF 8954597067493422955 AS o
WHERE o.order_id > 10;

SELECT
    cur.order_id,
    prev.status
FROM customer_orders AS cur
INNER JOIN customer_orders FOR VERSION AS OF 8954597067493422955 AS prev
    ON cur.order_id = prev.order_id;

CREATE OR REPLACE TABLE example.testdb.customer_orders AS
SELECT *
FROM example.testdb.customer_orders
FOR TIMESTAMP AS OF TIMESTAMP '2022-03-23 09:59:29.803 Europe/Vienna';
