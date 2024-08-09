-- Iceberg Spark DDL Create Table Statements https://iceberg.apache.org/docs/latest/spark-ddl/#create-table

CREATE TABLE prod.db.sample (
    id bigint COMMENT 'unique id',
    data string)
USING iceberg;

CREATE TABLE prod.db.sample (
    id bigint,
    data string,
    category string)
USING iceberg
PARTITIONED BY (category);

CREATE TABLE prod.db.sample (
    id bigint,
    data string,
    category string,
    ts timestamp)
USING iceberg
PARTITIONED BY (bucket(16, id), days(ts), category);

CREATE TABLE prod.db.sample
USING iceberg
PARTITIONED BY (part)
TBLPROPERTIES ('key'='value');
