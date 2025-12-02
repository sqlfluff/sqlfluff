CREATE TABLE db.foo
  (col1 integer, col2 string);

CREATE TABLE db.foo (
    col1 INT,
    col2 STRING,
    col3 DECIMAL(10,2)
) PARTITIONED BY (col4 INT);
