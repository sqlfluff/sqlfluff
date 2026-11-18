CREATE TABLE my_table (
    id INT,
    tags ARRAY<STRING NOT NULL>,
    attributes MAP<STRING, STRING NOT NULL>,
    details ROW<name STRING NOT NULL, count INT>,
    required_tags ARRAY<STRING NOT NULL> NOT NULL
) WITH (
    'connector' = 'kafka',
    'topic' = 'my-topic'
);
