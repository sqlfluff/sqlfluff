-- https://docs.snowflake.com/en/sql-reference/sql/create-storage-lifecycle-policy
CREATE STORAGE LIFECYCLE POLICY my_policy
AS (path STRING, last_modified TIMESTAMP_NTZ)
RETURNS BOOLEAN -> last_modified < DATEADD(day, -30, CURRENT_TIMESTAMP())
ARCHIVE_TIER = COLD
ARCHIVE_FOR_DAYS = 90
COMMENT = 'archive old files';

CREATE OR REPLACE STORAGE LIFECYCLE POLICY IF NOT EXISTS "My Policy"
AS (file_path STRING)
RETURNS BOOLEAN -> file_path LIKE '%.log'
ARCHIVE_TIER = COOL
WITH TAG (governance = 'retention', owner = 'platform');

CREATE STORAGE LIFECYCLE POLICY minimal_policy
AS (file_path STRING)
RETURNS BOOLEAN -> TRUE;

CREATE STORAGE LIFECYCLE POLICY tagged_without_with
AS (file_path STRING)
RETURNS BOOLEAN -> TRUE
TAG (team = 'data');
