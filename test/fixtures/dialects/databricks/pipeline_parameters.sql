-- Databricks Pipeline Parameters
-- https://docs.databricks.com/en/delta-live-tables/parameters.html

-- Parameter in FROM clause with catalog reference
SELECT
    *
FROM ${source_catalog}.silver.payments;

-- Parameter in FROM clause with full path
SELECT
    *
FROM ${source_catalog_main}.silver.payments
WHERE amount > 100;

-- Multiple parameters
SELECT
    *
FROM ${source_catalog}.${source_schema}.${source_table}
WHERE date > '2023-01-01';

-- Parameter in USE CATALOG
USE CATALOG ${target_catalog};

-- Parameter in CREATE TABLE
CREATE OR REFRESH STREAMING TABLE processed_data
AS SELECT
    transaction_id,
    amount,
    customer_id
FROM ${source_catalog}.raw.transactions;

-- Parameter in JOIN
SELECT
    a.id,
    b.name
FROM ${source_catalog}.schema1.table1 AS a
    INNER JOIN ${target_catalog}.schema2.table2 AS b
        ON a.id = b.id;

-- Parameter in materialized view
CREATE OR REFRESH MATERIALIZED VIEW aggregated_data
AS
SELECT
    customer_id,
    SUM(amount) AS total_amount
FROM ${source_catalog}.silver.payments
GROUP BY customer_id;

-- Mixed parameters (colon and pipeline dollar syntax)
SELECT
    *
FROM ${source_catalog}.silver.payments
WHERE
    customer_id = :customer_id
    AND amount > :min_amount;

-- Parameter in INSERT
INSERT INTO ${target_catalog}.gold.summary
SELECT
    date,
    COUNT(*) AS transaction_count
FROM ${source_catalog}.silver.payments
GROUP BY date;

-- Parameter in UPDATE
UPDATE ${target_catalog}.gold.customer_stats
SET last_updated = CURRENT_TIMESTAMP()
WHERE customer_id = :customer_id;

-- Parameter in DELETE
DELETE FROM ${target_catalog}.staging.temp_data
WHERE process_date < CURRENT_DATE() - INTERVAL 7 DAYS;

-- Parameter with IDENTIFIER clause
USE SCHEMA IDENTIFIER (${schema_name});

-- Parameter in CREATE CATALOG
CREATE CATALOG IF NOT EXISTS ${new_catalog};

-- Parameter in ALTER CATALOG
ALTER CATALOG ${source_catalog}
SET OWNER TO `data_team`;

-- Nested parameter usage in pipeline
CREATE OR REFRESH STREAMING TABLE customer_silver
AS
SELECT
    c.*,
    p.total_purchases
FROM STREAM (${bronze_catalog}.customers.raw_customers) AS c
    LEFT JOIN ${gold_catalog}.analytics.customer_purchases AS p
        ON c.customer_id = p.customer_id;
