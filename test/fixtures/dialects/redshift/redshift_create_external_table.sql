CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER
)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 STRING
)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 STRING
)
STORED AS ORC
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 STRING
)
STORED AS AVRO
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 STRING
)
STORED AS TEXTFILE
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 STRING
)
PARTITIONED BY (col3 integer)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 STRING
)
PARTITIONED BY (col3 INTEGER, col4 INTEGER)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
;
