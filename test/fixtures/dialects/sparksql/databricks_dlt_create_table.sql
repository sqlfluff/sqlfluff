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
FROM CLOUD_FILES("/databricks-datasets/retail-org/customers/", "csv");

CREATE OR REFRESH STREAMING LIVE TABLE customers_silver
AS SELECT
    a,
    b
FROM STREAM(live.customers_bronze);

CREATE OR REFRESH TEMPORARY LIVE TABLE filtered_data
AS SELECT
    a,
    b
FROM live.taxi_raw;

CREATE OR REFRESH TEMPORARY STREAMING LIVE TABLE customers_silver
AS SELECT
    a,
    b
FROM STREAM(live.customers_bronze);

CREATE OR REFRESH LIVE TABLE taxi_raw(
    a STRING COMMENT 'a',
    b INT COMMENT 'b',
    CONSTRAINT valid_a EXPECT (a IS NOT NULL),
    CONSTRAINT valid_b EXPECT (b > 0)
)
AS SELECT
    a,
    b
FROM JSON.`/databricks-datasets/nyctaxi/sample/json/`;
