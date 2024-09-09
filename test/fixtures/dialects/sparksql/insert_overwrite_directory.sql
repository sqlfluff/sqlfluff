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

WITH cte AS (
     SELECT
        *
     FROM test_table
)

INSERT OVERWRITE DIRECTORY 'destination_dir/path_to'
USING CSV
OPTIONS (
    sep '\t',
    header 'true',
    compression 'none',
    emptyValue ''
)

SELECT /*+ COALESCE(1) */ *
FROM cte;
