CREATE TABLE foo(
    col1 INT PRIMARY KEY,
    col2 BIGINT NOT NULL,
    col3 STRING,
    col4 STRING COMMENT 'Column 4'
)
COMMENT 'This is a test table'
STORED AS ORC;