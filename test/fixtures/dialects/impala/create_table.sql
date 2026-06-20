CREATE TABLE db.foo
  (col1 integer, col2 string);

CREATE TABLE db.foo (
    col1 INT,
    col2 STRING,
    col3 DECIMAL(10,2)
) PARTITIONED BY (col4 INT);

CREATE TABLE db.kudu_t (
    id INT PRIMARY KEY,
    val STRING NOT NULL
) PARTITION BY HASH (id) PARTITIONS 4
  STORED AS KUDU;

CREATE EXTERNAL TABLE db.like_t
  LIKE PARQUET '/data/sample.parquet'
  CACHED IN 'default_pool';

