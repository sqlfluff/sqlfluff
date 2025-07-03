CREATE TABLE my_table (
    id INT,
    name STRING,
    age INT
) WITH (
    'connector' = 'kafka',
    'topic' = 'my-topic'
);
