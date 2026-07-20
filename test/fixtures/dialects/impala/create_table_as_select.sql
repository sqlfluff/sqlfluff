CREATE TABLE db.ctas_table
  PARTITIONED BY (year INT)
  STORED AS PARQUET
  CACHED IN 'default_pool'
AS SELECT * FROM db.src;
