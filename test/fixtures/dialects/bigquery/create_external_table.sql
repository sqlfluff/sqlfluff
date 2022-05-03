CREATE EXTERNAL TABLE dataset.CsvTable OPTIONS (
  format = 'CSV',
  uris = ['gs://bucket/path1.csv', 'gs://bucket/path2.csv']
);

CREATE OR REPLACE EXTERNAL TABLE dataset.CsvTable
(
  x INT64,
  y STRING
)
OPTIONS (
  format = 'CSV',
  uris = ['gs://bucket/path1.csv'],
  field_delimiter = '|',
  max_bad_records = 5
);

CREATE EXTERNAL TABLE dataset.AutoHivePartitionedTable
WITH PARTITION COLUMNS
OPTIONS (
  uris=['gs://bucket/path/*'],
  format=csv,
  hive_partition_uri_prefix='gs://bucket/path'
);

CREATE EXTERNAL TABLE dataset.CustomHivePartitionedTable
WITH PARTITION COLUMNS (
  field_1 STRING, -- column order must match the external path
  field_2 INT64
)
OPTIONS (
  uris=['gs://bucket/path/*'],
  format=csv,
  hive_partition_uri_prefix='gs://bucket/path'
);

-- Test arbritary ordering of optional arguments
CREATE EXTERNAL TABLE dataset.CustomHivePartitionedTable
OPTIONS (
  uris=['gs://bucket/path/*'],
  format=csv,
  hive_partition_uri_prefix='gs://bucket/path'
)
WITH PARTITION COLUMNS (
  field_1 STRING, -- column order must match the external path
  field_2 INT64
);
