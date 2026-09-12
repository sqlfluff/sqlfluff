-- https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-flow
-- CREATE FLOW flow_name [ COMMENT comment ] AS
--   INSERT [ ONCE ] INTO target_table BY NAME [ replace_using_spec ] query

CREATE FLOW users_flow
AS INSERT INTO users BY NAME
SELECT * FROM STREAM(raw_data.users);

CREATE FLOW backfill_users
AS INSERT ONCE INTO users BY NAME
SELECT * FROM user_backfill_table;

-- https://docs.databricks.com/aws/en/ldp/flows-backfill spells the same
-- statement INSERT INTO ONCE.

CREATE FLOW registration_events_raw_backfill_2024
AS INSERT INTO ONCE registration_events_raw BY NAME
SELECT * FROM registration_events_raw_backfill;

CREATE FLOW payments_replace_flow
AS INSERT INTO payments_latest BY NAME
REPLACE USING (payment_id) SEQUENCE BY payment_date
SELECT
    payment_id,
    booking_id,
    status,
    payment_date
FROM STREAM(samples.wanderbricks.payments);

CREATE FLOW commented_flow COMMENT 'an append flow'
AS INSERT INTO users BY NAME
SELECT * FROM STREAM(raw_data.users);

-- ONCE is not a reserved word, so it is also a legal target table name.

CREATE FLOW once_flow
AS INSERT INTO once BY NAME
SELECT * FROM STREAM(raw_data.users);
