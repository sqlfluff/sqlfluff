-- https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-sql-ref.html#create-table

CREATE OR REFRESH LIVE TABLE taxi_raw
AS SELECT
    a,
    b
FROM JSON.`/databricks-datasets/nyctaxi/sample/json/`;

CREATE OR REFRESH LIVE TABLE filtered_data
AS SELECT
    a,
    b
FROM live.taxi_raw;

CREATE OR REFRESH STREAMING LIVE TABLE customers_bronze
AS SELECT
    a,
    b
FROM cloud_files("/databricks-datasets/retail-org/customers/", "csv");

CREATE OR REFRESH STREAMING LIVE TABLE customers_silver
AS SELECT
    a,
    b
FROM stream(live.customers_bronze);

CREATE OR REFRESH TEMPORARY LIVE TABLE filtered_data
AS SELECT
    a,
    b
FROM live.taxi_raw;

CREATE OR REFRESH TEMPORARY STREAMING LIVE TABLE customers_silver
AS SELECT
    a,
    b
FROM stream(live.customers_bronze);
