-- https://docs.snowflake.com/en/sql-reference/sql/create-storage-lifecycle-policy
CREATE STORAGE LIFECYCLE POLICY my_policy
AS (path STRING, last_modified TIMESTAMP_NTZ)
RETURNS BOOLEAN -> last_modified < DATEADD(day, -30, CURRENT_TIMESTAMP())
ARCHIVE_TIER = COLD
ARCHIVE_FOR_DAYS = 90
COMMENT = 'archive old files';

-- The example from the docs, whose body is a compound expression.
CREATE STORAGE LIFECYCLE POLICY example_policy
AS (event_ts TIMESTAMP, account_id NUMBER)
RETURNS BOOLEAN ->
    event_ts < DATEADD(DAY, -60, CURRENT_TIMESTAMP())
    AND EXISTS (SELECT 1 FROM closed_accounts WHERE id = account_id)
ARCHIVE_TIER = COOL
ARCHIVE_FOR_DAYS = 180;

-- OR REPLACE and IF NOT EXISTS are mutually exclusive, so they are covered
-- separately.
CREATE OR REPLACE STORAGE LIFECYCLE POLICY "My Policy"
AS (file_path STRING)
RETURNS BOOLEAN -> file_path LIKE '%.log'
ARCHIVE_TIER = COOL
WITH TAG (governance = 'retention', owner = 'platform');

CREATE STORAGE LIFECYCLE POLICY IF NOT EXISTS minimal_policy
AS (file_path STRING)
RETURNS BOOLEAN -> TRUE;

CREATE STORAGE LIFECYCLE POLICY tagged_without_with
AS (file_path STRING)
RETURNS BOOLEAN -> TRUE
TAG (team = 'data');
-- A policy name may be schema- or database-qualified; the docs say the policy is
-- created "in the current or specified schema".
CREATE STORAGE LIFECYCLE POLICY my_db.my_schema.qualified_policy
AS (file_path STRING)
RETURNS BOOLEAN -> TRUE;
