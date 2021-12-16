CREATE TABLE new_foo
   ROW FORMAT SERDE "org.apache.hadoop.hive.serde2.columnar.ColumnarSerDe"
   STORED AS RCFile
   AS
SELECT (col1 % 1024) col, concat(col1, col2) col12
FROM foo;
