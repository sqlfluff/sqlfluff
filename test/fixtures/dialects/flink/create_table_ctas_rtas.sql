CREATE TABLE my_ctas_table
WITH (
    'connector' = 'kafka',
    'topic' = 'my-topic'
)
AS
SELECT
    id,
    name,
    age
FROM source_table;

CREATE TABLE my_ctas_table (
    extra_desc STRING,
    quantity DOUBLE,
    cost AS price * quantity,
    WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'my-topic'
)
AS
SELECT
    id,
    price,
    quantity,
    order_time
FROM source_table;

CREATE TABLE my_ctas_table (
    order_time,
    price,
    quantity,
    id
) WITH (
    'connector' = 'kafka',
    'topic' = 'my-topic'
)
AS
SELECT
    id,
    price,
    quantity,
    order_time
FROM source_table;

CREATE TABLE my_ctas_table (
    PRIMARY KEY (id) NOT ENFORCED
) DISTRIBUTED BY (id) INTO 4 BUCKETS
AS
SELECT
    id,
    name
FROM source_table;

CREATE TABLE my_dist_part_table (
    id BIGINT,
    dt STRING
) DISTRIBUTED BY HASH (id) INTO 4 BUCKETS
PARTITIONED BY (dt)
WITH (
    'connector' = 'filesystem'
);

REPLACE TABLE my_rtas_table (
    extra_desc STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'my-topic'
)
AS
SELECT
    id,
    name
FROM source_table;

CREATE OR REPLACE TABLE my_rtas_table
WITH (
    'connector' = 'kafka',
    'topic' = 'my-topic'
)
AS
SELECT
    id,
    name
FROM source_table;
