-- Append flows, taken from
-- https://docs.databricks.com/aws/en/ldp/flow-examples

CREATE FLOW
  customers_west
AS INSERT INTO
  customers BY NAME
SELECT * FROM stream(customers_west_raw);

CREATE FLOW
  customers_east
AS INSERT INTO
  customers BY NAME
SELECT * FROM stream(customers_east_raw);

-- Backfill flows run once, taken from
-- https://docs.databricks.com/aws/en/ldp/flows-backfill

CREATE FLOW
  customers_backfill
AS INSERT INTO ONCE
  customers BY NAME
SELECT * FROM customers_historical;

-- The reference grammar spells the same thing as `INSERT [ONCE] INTO`, see
-- https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-flow

CREATE FLOW
  customers_backfill_alt
AS INSERT ONCE INTO
  customers BY NAME
SELECT * FROM customers_historical;

-- With a comment and a `REPLACE USING` spec.

CREATE FLOW customers_replace
COMMENT 'replace matching rows'
AS INSERT INTO customers BY NAME
REPLACE USING (customer_id, region) SEQUENCE BY sequence_num
SELECT * FROM stream(customers_updates);
