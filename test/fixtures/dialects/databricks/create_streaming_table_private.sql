-- `PRIVATE` streaming tables are internal to the pipeline, see
-- https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-streaming-table

CREATE PRIVATE STREAMING TABLE raw_customers (customer_id BIGINT);

CREATE OR REFRESH PRIVATE STREAMING TABLE staged_customers (
    customer_id BIGINT,
    region STRING
);

CREATE OR REFRESH PRIVATE STREAMING TABLE filtered_customers
AS SELECT * FROM stream(raw_customers) WHERE region IS NOT NULL;
