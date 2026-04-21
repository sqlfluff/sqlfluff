-- Simple aggregate function
CREATE OR REPLACE AGGREGATE FUNCTION mydataset.MEDIAN(
  value FLOAT64
) RETURNS FLOAT64
OPTIONS (description = "Calculates the median value")
AS (
  mydataset.GET_QUANTILE(value, 50)
);

-- Aggregate function with NOT AGGREGATE parameter
CREATE OR REPLACE AGGREGATE FUNCTION mydataset.GET_QUANTILE(
  value FLOAT64,
  percentile INT64 NOT AGGREGATE
) RETURNS FLOAT64
OPTIONS (description = "Calculates approximate quantiles")
AS (
  IF(
    percentile IS NULL OR percentile < 0 OR percentile > 100,
    NULL,
    APPROX_QUANTILES(value, 100)[SAFE_OFFSET(percentile)]
  )
);

-- Aggregate function returning STRUCT
CREATE OR REPLACE AGGREGATE FUNCTION mydataset.BUCKET_AGG(
  value FLOAT64,
  ts TIMESTAMP
) RETURNS STRUCT<
  total FLOAT64,
  avg_value FLOAT64,
  min_value FLOAT64,
  max_value FLOAT64,
  num_values INT64,
  min_ts TIMESTAMP,
  max_ts TIMESTAMP
>
OPTIONS (description = "Aggregates raw data for bucket generation")
AS (
  STRUCT(
    SUM(value) AS total,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(value) AS num_values,
    MIN(ts) AS min_ts,
    MAX(ts) AS max_ts
  )
);

-- Aggregate function with IF NOT EXISTS
CREATE AGGREGATE FUNCTION IF NOT EXISTS mydataset.SAFE_SUM(
  value FLOAT64
) RETURNS FLOAT64
AS (
  SUM(IF(ABS(value) <= 1e300, value, NULL))
);
