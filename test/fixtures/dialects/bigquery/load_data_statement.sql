LOAD DATA INTO mydataset.table1
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/file.avro']
  );

LOAD DATA INTO `myproject.mydataset.table1`
  FROM FILES(
    format='CSV',
    uris = ['gs://bucket/path/file1.csv', 'gs://bucket/path/file2.csv']
  );

LOAD DATA INTO mydataset.table1(x INT64, y STRING)
  FROM FILES(
    skip_leading_rows=1,
    format='CSV',
    uris = ['gs://bucket/path/file.csv']
  );

LOAD DATA INTO mydataset.table1
  OPTIONS(
    description="my table",
    expiration_timestamp="2025-01-01 00:00:00 UTC"
  )
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/file.avro']
  );

LOAD DATA OVERWRITE mydataset.table1
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/file.avro']
  );

LOAD DATA INTO TEMP TABLE mydataset.table1
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/file.avro']
  );

LOAD DATA INTO TEMP TABLE my_tmp_table
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/file.avro']
  );

LOAD DATA INTO mydataset.table1
  PARTITION BY transaction_date
  CLUSTER BY customer_id
  OPTIONS(
    partition_expiration_days=3
  )
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/file.avro']
  );

LOAD DATA INTO mydataset.table1
PARTITIONS(_PARTITIONTIME = TIMESTAMP '2016-01-01')
  PARTITION BY _PARTITIONTIME
  FROM FILES(
    format = 'AVRO',
    uris = ['gs://bucket/path/file.avro']
  )

LOAD DATA INTO mydataset.table1
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/*'],
    hive_partition_uri_prefix='gs://bucket/path'
  )
  WITH PARTITION COLUMNS(
    field_1 STRING, -- column order must match the external path
    field_2 INT64
  )

LOAD DATA INTO mydataset.table1
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/*'],
    hive_partition_uri_prefix='gs://bucket/path'
  )
  WITH PARTITION COLUMNS

-- This query returns an error in BigQuery.
LOAD DATA INTO mydataset.table1
  (
    x INT64, -- column_list is given but the partition column list is missing
    y STRING
  )
  FROM FILES(
    format='AVRO',
    uris = ['gs://bucket/path/*'],
    hive_partition_uri_prefix='gs://bucket/path'
  )
  WITH PARTITION COLUMNS

LOAD DATA INTO mydataset.testparquet
  FROM FILES (
    uris = ['s3://test-bucket/sample.parquet'],
    format = 'PARQUET'
  )
  WITH CONNECTION `aws-us-east-1.test-connection`

LOAD DATA INTO mydataset.test_csv (Number INT64, Name STRING, Time DATE)
  PARTITION BY Time
  FROM FILES (
    format = 'CSV', uris = ['azure://test.blob.core.windows.net/container/sampled*'],
    skip_leading_rows=1
  )
  WITH CONNECTION `azure-eastus2.test-connection`

LOAD DATA OVERWRITE mydataset.testparquet
  FROM FILES (
    uris = ['s3://test-bucket/sample.parquet'],
    format = 'PARQUET'
  )
  WITH CONNECTION `aws-us-east-1.test-connection`
