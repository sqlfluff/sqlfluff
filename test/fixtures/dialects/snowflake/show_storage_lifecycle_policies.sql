-- https://docs.snowflake.com/en/sql-reference/sql/show-storage-lifecycle-policies

-- Show all
SHOW STORAGE LIFECYCLE POLICIES;

-- Show with LIKE filter
SHOW STORAGE LIFECYCLE POLICIES LIKE '%retention%';

-- Show in account
SHOW STORAGE LIFECYCLE POLICIES IN ACCOUNT;

-- Show in database
SHOW STORAGE LIFECYCLE POLICIES IN DATABASE my_db;

-- Show in schema
SHOW STORAGE LIFECYCLE POLICIES IN SCHEMA my_db.my_schema;
