CREATE TABLE test_table (
    data_info ROW<info STRING>,
    name STRING,
    score DOUBLE
) WITH (
    connector == 'test-connector',
    environment == 'development'
);
