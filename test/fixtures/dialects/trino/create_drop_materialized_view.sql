CREATE MATERIALIZED VIEW test AS
SELECT *
FROM orders
;

CREATE MATERIALIZED VIEW IF NOT EXISTS test AS
SELECT *
FROM orders
;

CREATE OR REPLACE MATERIALIZED VIEW test AS
SELECT *
FROM orders
;

CREATE MATERIALIZED VIEW orders_by_date
COMMENT 'Summary of orders by date'
AS
SELECT orderdate, sum(totalprice) AS price
FROM orders
GROUP BY orderdate
;

CREATE MATERIALIZED VIEW orders_by_date
GRACE PERIOD INTERVAL '0' DAY
AS
SELECT orderdate, sum(totalprice) AS price
FROM orders
GROUP BY orderdate
;

CREATE MATERIALIZED VIEW orders_by_date
WITH (
    partitioned_on = ARRAY ['ds']
)
AS
SELECT orderdate, sum(totalprice) AS price
FROM orders
GROUP BY orderdate
;

CREATE OR REPLACE MATERIALIZED VIEW IF NOT EXISTS orders_by_date
GRACE PERIOD INTERVAL '1' DAY
COMMENT 'Summary of orders by date'
WITH (
    partitioned_on = ARRAY ['ds']
)
AS
SELECT orderdate, sum(totalprice) AS price
FROM orders
GROUP BY orderdate
;

DROP MATERIALIZED VIEW test
;

DROP MATERIALIZED VIEW IF EXISTS test
;
