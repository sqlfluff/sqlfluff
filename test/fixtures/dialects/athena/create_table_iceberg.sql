create table my_database.my_table(
    field_1 string,
    field_2 int,
    field_3 float
) PARTITIONED BY (field_1)
  LOCATION 's3://athena-examples-myregion/my_table/'
  TBLPROPERTIES ( 'table_type' = 'ICEBERG' );

-- Example from Athena Docs:
-- https://docs.aws.amazon.com/athena/latest/ug/querying-iceberg-creating-tables.html
CREATE TABLE iceberg_table (id bigint, data string, category string)
  PARTITIONED BY (category, bucket(16, id))
  LOCATION 's3://amzn-s3-demo-bucket/your-folder/'
  TBLPROPERTIES ( 'table_type' = 'ICEBERG' );
