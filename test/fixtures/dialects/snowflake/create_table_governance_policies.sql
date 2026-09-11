-- Data governance policies on CREATE TABLE
-- https://docs.snowflake.com/en/sql-reference/sql/create-table

CREATE TABLE t_agg (a INT, b INT)
WITH AGGREGATION POLICY my_agg_policy;

CREATE TABLE t_agg_entity (a INT, b INT)
WITH AGGREGATION POLICY my_db.my_schema.my_agg_policy ENTITY KEY (a, b);

CREATE TABLE t_agg_no_with (a INT)
AGGREGATION POLICY my_agg_policy ENTITY KEY (a);

CREATE TABLE t_join (a INT, b INT)
WITH JOIN POLICY my_join_policy;

CREATE TABLE t_join_keys (a INT, b INT)
WITH JOIN POLICY my_db.my_schema.my_join_policy ALLOWED JOIN KEYS (a, b);

CREATE TABLE t_projection (
    c1 STRING WITH PROJECTION POLICY my_projection_policy,
    c2 STRING PROJECTION POLICY my_db.my_schema.other_policy,
    c3 STRING WITH MASKING POLICY my_masking_policy WITH PROJECTION POLICY my_projection_policy
);

CREATE TABLE t_storage_lifecycle (a INT, ts TIMESTAMP_NTZ)
WITH STORAGE LIFECYCLE POLICY my_slc_policy ON (ts);

CREATE TABLE t_storage_lifecycle_no_with (a INT, ts TIMESTAMP_NTZ)
STORAGE LIFECYCLE POLICY my_db.my_schema.my_slc_policy ON (ts, a);

CREATE TABLE t_contact (a INT)
WITH CONTACT (STEWARD = my_contact);

CREATE TABLE t_contacts (a INT)
WITH CONTACT (STEWARD = my_db.my_schema.steward_contact, SUPPORT = support_contact, ACCESS_APPROVAL = approver_contact);

CREATE TABLE t_copy_tags CLONE source_table COPY TAGS;

CREATE TABLE t_copy_grants_and_tags CLONE source_table COPY GRANTS COPY TAGS;

CREATE OR REPLACE TABLE t_all_policies (
    id INT,
    email STRING WITH MASKING POLICY email_mask,
    secret STRING WITH PROJECTION POLICY no_project
)
COPY GRANTS
COPY TAGS
WITH ROW ACCESS POLICY my_rap ON (id)
WITH AGGREGATION POLICY my_agg ENTITY KEY (id)
WITH JOIN POLICY my_join ALLOWED JOIN KEYS (id)
WITH TAG (cost_center = 'sales')
WITH CONTACT (STEWARD = data_steward)
COMMENT = 'table with the full governance surface'
AS
SELECT
    id,
    email,
    secret
FROM source_table;
