-- From BigQuery Docs:
-- https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#create_table_function_statement
CREATE OR REPLACE TABLE FUNCTION mydataset.names_by_year(y INT64)
RETURNS TABLE<name STRING, year INT64, total INT64>
AS
  SELECT year, name, SUM(number) AS total
  FROM `bigquery-public-data.usa_names.usa_1910_current`
  WHERE year = y
  GROUP BY year, name;

CREATE OR REPLACE TABLE FUNCTION analytics_sandbox.test_tvf(
  input_table TABLE<sales INT64, item STRING>,
  item_name STRING
) AS (
  SELECT
    SUM(sales) AS total_sales,
    item
  FROM input_table
  WHERE item = item_name
  GROUP BY item
);
