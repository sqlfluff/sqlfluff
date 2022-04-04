INSERT OVERWRITE DIRECTORY '/tmp/destination'
USING PARQUET
OPTIONS (col1 = "1", col2 = "2", col3 = 'test', "user" = "a person")
SELECT a FROM test_table;

INSERT OVERWRITE DIRECTORY
USING PARQUET
OPTIONS (
    path = '/tmp/destination', col1 = "1", col2 = "2", col3 = 'test'
)
SELECT a FROM test_table;

INSERT OVERWRITE DIRECTORY
USING PARQUET
OPTIONS (path '/tmp/destination', col1 1, col2 2, col3 'test')
SELECT a FROM test_table;

INSERT OVERWRITE DIRECTORY '/tmp/destination'
USING PARQUET
OPTIONS (col1 1, col2 2, col3 'test')
SELECT a FROM test_table;
