CREATE TABLE my_table (
    id INT,
    event_time TIMESTAMP(3),
    processing_time TIMESTAMP_LTZ(3),
    updated_at TIMESTAMP(6)
) WITH (
    'connector' = 'kafka'
);
