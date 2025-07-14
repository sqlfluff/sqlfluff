CREATE TABLE a (
    str varchar
);

create table if not exists foo.bar.baz
(
date_nk date,
date_ts timestamp,
site varchar(30),
partition_date date
)
with (
format = 'parquet',
partitioned_by = array ['partition_date']
);

CREATE TABLE orders (
  orderkey bigint,
  orderstatus varchar,
  totalprice double,
  orderdate date
)
WITH (format = 'ORC')
;

CREATE TABLE IF NOT EXISTS orders (
  orderkey bigint,
  orderstatus varchar,
  totalprice double COMMENT 'Price in cents.',
  shipmentstatus varchar not null,
  orderdate date
)
COMMENT 'A table to keep track of orders.'
;

CREATE TABLE bigger_orders (
  another_orderkey bigint,
  LIKE orders,
  another_orderdate date
)
;

CREATE TABLE orders_column_aliased (order_date, total_price)
AS
SELECT orderdate, totalprice
FROM orders
;

CREATE TABLE orders_by_date
COMMENT 'Summary of orders by date'
WITH (format = 'ORC')
AS
SELECT orderdate, sum(totalprice) AS price
FROM orders
GROUP BY orderdate
;

CREATE TABLE IF NOT EXISTS orders_by_date AS
SELECT orderdate, sum(totalprice) AS price
FROM orders
GROUP BY orderdate
;

CREATE TABLE empty_nation AS
SELECT *
FROM nation
WITH NO DATA
;

CREATE TABLE structual_types (
  array_of_ints array(integer),
  map_of_ints map(integer, integer),
  row_of_ints row(a integer, b integer, c integer)
);
