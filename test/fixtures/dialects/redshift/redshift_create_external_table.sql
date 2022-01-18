CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER
)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 TEXT
)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 TEXT
)
STORED AS ORC
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 TEXT
)
STORED AS AVRO
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 TEXT
)
STORED AS TEXTFILE
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 TEXT
)
PARTITIONED BY (col3 integer)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER,
    col2 TEXT
)
PARTITIONED BY (col3 INTEGER, col4 INTEGER)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
;

CREATE EXTERNAL TABLE external_schema.table_name (
    col1 INTEGER
)
STORED AS PARQUET
LOCATION 's3://bucket/folder'
TABLE PROPERTIES ('some_property1'='some_value1', 'some_property2'='some_value2')
;
