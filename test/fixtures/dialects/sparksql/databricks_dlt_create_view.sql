-- https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-sql-ref.html#create-view

CREATE TEMPORARY LIVE VIEW filtered_data
AS SELECT
    a,
    b
FROM live.taxi_raw;

CREATE TEMPORARY STREAMING LIVE VIEW customers_silver
AS SELECT
    a,
    b
FROM stream(live.customers_bronze);

CREATE TEMPORARY LIVE VIEW filtered_data(
    a COMMENT 'a',
    b COMMENT 'b',
    CONSTRAINT valid_a EXPECT (a IS NOT NULL),
    CONSTRAINT valid_b EXPECT (b > 0)
)
AS SELECT
    a,
    b
FROM live.taxi_raw;

CREATE OR REFRESH MATERIALIZED VIEW temp_table
AS
SELECT 1 AS ID;

CREATE OR REFRESH MATERIALIZED VIEW dlt_view (
    a STRING COMMENT 'a',
    b TIMESTAMP COMMENT 'b'
)
COMMENT 'DLT materialized view'
AS SELECT
    a,
    b
FROM live.dlt_bronze;

CREATE OR REFRESH MATERIALIZED VIEW my_dlt_mat_view (
    col1 STRING COMMENT 'Dummy column 1',
    col2 BIGINT COMMENT 'Dummy column 2',
    col3 BOOLEAN COMMENT 'Dummy column 3'
)
PARTITIONED BY (col1)
COMMENT 'Example simplified materialized view with dummy fields.'
TBLPROPERTIES ('quality' = 'gold')
AS SELECT
    col1,
    col2,
    col3
FROM my_source_table;

CREATE OR REFRESH MATERIALIZED VIEW my_dlt_mat_view (
    col1 STRING COMMENT 'Dummy column 1',
    col2 BIGINT COMMENT 'Dummy column 2',
    col3 BOOLEAN COMMENT 'Dummy column 3'
)
CLUSTER BY (col1)
COMMENT 'Example simplified materialized view with dummy fields.'
TBLPROPERTIES ('quality' = 'gold')
AS SELECT
    col1,
    col2,
    col3
FROM my_source_table;
