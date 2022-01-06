CREATE EXTERNAL TABLE
external_schema.table_name
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS
SELECT col1, col2 FROM external_schema.source_table
;

CREATE EXTERNAL TABLE
external_schema.table_name
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS
SELECT * FROM external_schema.source_table
;

CREATE EXTERNAL TABLE
external_schema.table_name
PARTITIONED BY (col1 integer)
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS
SELECT col1, col2 FROM external_schema.source_table
;

CREATE EXTERNAL TABLE
external_schema.table_name
PARTITIONED BY (col1 integer)
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS
SELECT * FROM external_schema.source_table
;

CREATE EXTERNAL TABLE
external_schema.table_name
PARTITIONED BY (col1 integer, col2 integer)
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS
SELECT col1, col2 FROM external_schema.source_table
;

CREATE EXTERNAL TABLE
external_schema.table_name
PARTITIONED BY (col1 integer, col2 integer)
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS
SELECT * FROM external_schema.source_table
;

CREATE EXTERNAL TABLE
external_schema.table_name
PARTITIONED BY (col1 integer, col2 integer)
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS (
    SELECT col1, col2 FROM external_schema.source_table
)
;
