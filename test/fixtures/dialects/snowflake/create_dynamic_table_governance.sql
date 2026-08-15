-- Data governance clauses on CREATE DYNAMIC TABLE
-- https://docs.snowflake.com/en/sql-reference/sql/create-dynamic-table

CREATE OR REPLACE DYNAMIC TABLE dt_copy_tags
TARGET_LAG = '5 minutes'
WAREHOUSE = wh
COPY TAGS
AS
SELECT a FROM b;

CREATE DYNAMIC TABLE dt_aggregation_policy
TARGET_LAG = '5 minutes'
WAREHOUSE = wh
WITH AGGREGATION POLICY ap ENTITY KEY (c1)
AS
SELECT c1 FROM b;

CREATE DYNAMIC TABLE dt_projection_policy (
    c1 STRING WITH PROJECTION POLICY pp,
    c2 STRING WITH MASKING POLICY mp COMMENT 'masked column'
)
TARGET_LAG = '5 minutes'
WAREHOUSE = wh
AS
SELECT c1, c2 FROM b;

CREATE DYNAMIC TABLE dt_contact
TARGET_LAG = DOWNSTREAM
WAREHOUSE = wh
WITH CONTACT (STEWARD = data_steward)
AS
SELECT a FROM b;
