CREATE TABLE orders (
    order_id INT,
    price DECIMAL(32, 2),
    currency STRING,
    order_time TIMESTAMP(3)
) DISTRIBUTED BY HASH(order_id) INTO 4 BUCKETS;

CREATE TABLE orders_range (
    order_id INT,
    price DECIMAL(32, 2)
) DISTRIBUTED BY RANGE(order_id) INTO 8 BUCKETS;

CREATE TABLE orders_implicit (
    order_id INT
) DISTRIBUTED BY (order_id) INTO 2 BUCKETS;

CREATE TABLE orders_buckets_only (
    order_id INT
) DISTRIBUTED INTO 16 BUCKETS;

CREATE TABLE orders_no_buckets (
    order_id INT
) DISTRIBUTED BY HASH(order_id);
