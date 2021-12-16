CREATE EXTERNAL TABLE IF NOT EXISTS foo (
    col1 int,
    col2 string
)
PARTITIONED BY (col3 string, col4 date)
LOCATION 'hdfs://path';
