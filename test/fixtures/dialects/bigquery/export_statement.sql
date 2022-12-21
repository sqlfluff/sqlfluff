EXPORT DATA
WITH CONNECTION PROJECT_ID.LOCATION.CONNECTION_ID
OPTIONS(
    uri='gs://bucket/folder/*.csv',
    format='CSV',
    overwrite=true,
    header=true,
    field_delimiter=';'
  )
AS SELECT field1, field2 FROM mydataset.table1 ORDER BY field1;

EXPORT DATA
WITH CONNECTION `PROJECT_ID.LOCATION.CONNECTION_ID`
OPTIONS(
    uri='gs://bucket/folder/*.csv',
    format='CSV',
    overwrite=true,
    header=true,
    field_delimiter=';'
  )
AS SELECT field1, field2 FROM mydataset.table1 ORDER BY field1;


EXPORT DATA OPTIONS(
  uri='gs://bucket/folder/*.csv',
  format='CSV',
  overwrite=true,
  header=true,
  field_delimiter=';') AS
SELECT field1, field2 FROM mydataset.table1 ORDER BY field1 LIMIT 10;

EXPORT DATA OPTIONS(
  uri="gs://bucket/folder/*.csv",
  format="CSV",
  overwrite=true,
  header=true,
  field_delimiter=';') AS
SELECT field1, field2 FROM mydataset.table1 ORDER BY field1 LIMIT 10;

EXPORT DATA OPTIONS(
  uri='gs://bucket/folder/*',
  format='AVRO',
  compression='SNAPPY') AS
SELECT field1, field2 FROM mydataset.table1 ORDER BY field1 LIMIT 10;

EXPORT DATA OPTIONS(
  uri='gs://bucket/folder/*',
  format='PARQUET',
  overwrite=true) AS
SELECT field1, field2 FROM mydataset.table1 ORDER BY field1 LIMIT 10;

EXPORT DATA OPTIONS(
  uri='gs://bucket/folder/*.csv',
  format='CSV',
  overwrite=true,
  header=true,
  field_delimiter=';') AS
WITH cte AS (
    SELECT field1, field2
    FROM mydataset.table1
    ORDER BY field1
    LIMIT 10
)
SELECT *
FROM cte;
