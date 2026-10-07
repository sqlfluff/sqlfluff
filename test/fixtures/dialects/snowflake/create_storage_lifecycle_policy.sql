-- https://docs.snowflake.com/en/sql-reference/sql/create-storage-lifecycle-policy

-- Basic storage lifecycle policy
CREATE STORAGE LIFECYCLE POLICY my_slp
  AS (reference_col DATE)
  RETURNS BOOLEAN ->
    reference_col < DATEADD(DAY, -90, CURRENT_DATE());

-- Fully qualified name
CREATE STORAGE LIFECYCLE POLICY my_db.my_schema.my_slp
  AS (reference_col TIMESTAMP_NTZ)
  RETURNS BOOLEAN ->
    reference_col < DATEADD(DAY, -1095, CURRENT_DATE());

-- OR REPLACE
CREATE OR REPLACE STORAGE LIFECYCLE POLICY my_slp
  AS (reference_col DATE)
  RETURNS BOOLEAN ->
    reference_col < DATEADD(DAY, -30, CURRENT_DATE());

-- IF NOT EXISTS
CREATE STORAGE LIFECYCLE POLICY IF NOT EXISTS my_slp
  AS (reference_col DATE)
  RETURNS BOOLEAN ->
    reference_col < DATEADD(DAY, -7, CURRENT_DATE());

-- With ARCHIVE_TIER and ARCHIVE_FOR_DAYS (from Snowflake docs example)
CREATE STORAGE LIFECYCLE POLICY example_policy
  AS (event_ts TIMESTAMP, account_id NUMBER)
  RETURNS BOOLEAN ->
    event_ts < DATEADD(DAY, -60, CURRENT_TIMESTAMP())
  ARCHIVE_TIER = COOL
  ARCHIVE_FOR_DAYS = 180;

-- With COMMENT
CREATE STORAGE LIFECYCLE POLICY my_slp
  AS (reference_col DATE)
  RETURNS BOOLEAN ->
    reference_col < DATEADD(DAY, -365, CURRENT_DATE())
  COMMENT = 'Expire rows older than 1 year';

-- With ARCHIVE_TIER = COLD
CREATE STORAGE LIFECYCLE POLICY cold_archive_slp
  AS (reference_col DATE)
  RETURNS BOOLEAN ->
    reference_col < DATEADD(DAY, -730, CURRENT_DATE())
  ARCHIVE_TIER = COLD
  ARCHIVE_FOR_DAYS = 365
  COMMENT = 'Archive to cold tier for 1 year before expiry';
