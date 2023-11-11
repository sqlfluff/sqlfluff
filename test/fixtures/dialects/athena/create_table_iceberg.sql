create table my_database.my_table(
    field_1 string,
    field_2 int,
    field_3 float
)  PARTITIONED BY (field_1)
  LOCATION 's3://athena-examples-myregion/my_table/'
  TBLPROPERTIES ( 'table_type' = 'ICEBERG' );

CREATE TABLE iceberg_table WITH (
  format = 'PARQUET',
  table_type ='ICEBERG',
  partitioning = ARRAY['column_name'],
  external_location ='s3://DOC-EXAMPLE-BUCKET/tables/iceberg_table/'
) AS
SELECT
  *
FROM
  table_name;
