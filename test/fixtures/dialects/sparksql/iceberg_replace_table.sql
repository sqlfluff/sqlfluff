-- Iceberg Spark DDL Create Table Statements https://iceberg.apache.org/docs/latest/spark-ddl/#replace-table--as-select

REPLACE TABLE prod.db.sample
USING iceberg;

REPLACE TABLE prod.db.sample
USING iceberg
PARTITIONED BY (part)
TBLPROPERTIES ('key'='value');

CREATE OR REPLACE TABLE prod.db.sample
USING iceberg;
