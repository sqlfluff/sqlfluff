CREATE TABLE foo(
    col1 INT PRIMARY KEY,
    col2 INTEGER NOT NULL,
    col3 BIGINT NOT NULL,
    col4 STRING,
    col5 STRING COMMENT 'Column 5'
)
COMMENT 'This is a test table'
STORED AS ORC;
