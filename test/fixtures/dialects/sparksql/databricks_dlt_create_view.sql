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
