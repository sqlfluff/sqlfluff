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

create external table spectrum.sales(
salesid integer,
saledate date,
qtysold smallint,
pricepaid decimal(8,2),
saletime timestamp)
row format delimited
fields terminated by '\t'
stored as textfile
location 's3://awssampledbuswest2/tickit/spectrum/sales/'
table properties ('numRows'='170000');

create external table spectrum.cloudtrail_json (
event_version int,
event_id bigint,
event_time timestamp,
event_type varchar(10),
recipientaccountid bigint)
row format serde 'org.openx.data.jsonserde.JsonSerDe'
with serdeproperties (
'dots.in.keys' = 'true',
'mapping.requesttime' = 'requesttimestamp'
)
stored as textfile
location 's3://mybucket/json/cloudtrail';

CREATE EXTERNAL TABLE schema_spectrum_uddh.soccer_league
(
  league_rank smallint,
  club_name   varchar(15),
  league_spi  decimal(6,2),
  league_nspi smallint
)
ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n\l'
stored as textfile
LOCATION 's3://spectrum-uddh/league/'
table properties ('skip.header.line.count'='1');

CREATE EXTERNAL TABLE tbl1 (col1 int, col2 varchar(10))
ROW FORMAT SERDE 'com.amazon.ionhiveserde.IonHiveSerDe'
STORED AS
INPUTFORMAT 'com.amazon.ionhiveserde.formats.IonInputFormat'
OUTPUTFORMAT 'com.amazon.ionhiveserde.formats.IonOutputFormat'
LOCATION 's3://s3-bucket/prefix';

CREATE EXTERNAL TABLE spectrum.partitioned_lineitem
PARTITIONED BY (l_shipdate, l_shipmode)
STORED AS parquet
LOCATION 'S3://mybucket/cetas/partitioned_lineitem/'
AS SELECT 1;
