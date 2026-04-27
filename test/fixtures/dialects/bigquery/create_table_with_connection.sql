-- BigLake / Iceberg table with CONNECTION
CREATE OR REPLACE TABLE my_dataset.my_table
(
  id STRING,
  name STRING
)
CLUSTER BY id
WITH CONNECTION `europe-west4.my_connection`
OPTIONS (
  file_format = "PARQUET",
  table_format = "ICEBERG",
  storage_uri = "gs://my-bucket/path"
)
AS
SELECT "1" AS id, "test" AS name;

-- WITH CONNECTION without AS
CREATE TABLE IF NOT EXISTS my_dataset.my_table
(
  id STRING
)
WITH CONNECTION `my-project.us.my_connection`
OPTIONS (
  file_format = "PARQUET",
  table_format = "ICEBERG",
  storage_uri = "gs://my-bucket/path"
);
