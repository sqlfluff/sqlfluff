CREATE TABLE my_table (
    id INT,
    name STRING,
    full_name AS CONCAT(name, '_suffix'),
    kafka_offset BIGINT METADATA FROM 'offset'
) WITH (
    'connector' = 'kafka'
);
