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

CREATE EXTERNAL TABLE
external_schema.table_name
PARTITIONED BY (col1 integer, col2 integer)
ROW FORMAT DELIMITED LINES TERMINATED BY '\007'
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS (
    SELECT col1, col2 FROM external_schema.source_table
)
;

CREATE EXTERNAL TABLE
external_schema.table_name
PARTITIONED BY (col1 integer, col2 integer)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\007'
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
AS (
    SELECT col1, col2 FROM external_schema.source_table
)
;

CREATE EXTERNAL TABLE
external_schema.table_name
STORED AS PARQUET
LOCATION 's3://bucket/folder/'
TABLE PROPERTIES ('some_property1'='some_value1', 'some_property2'='some_value2')
AS
SELECT col1, col2 FROM external_schema.source_table
;

CREATE EXTERNAL TABLE spectrum.partitioned_lineitem
PARTITIONED BY (l_shipdate date, l_shipmode varchar(24))
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n\l'
STORED AS textfile
LOCATION 'S3://mybucket/cetas/partitioned_lineitem/'
AS SELECT l_orderkey, l_shipmode, l_shipdate, l_partkey FROM local_table;
