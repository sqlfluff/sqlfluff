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
