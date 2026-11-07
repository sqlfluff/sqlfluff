-- https://docs.snowflake.com/en/sql-reference/sql/drop-storage-lifecycle-policy

-- Basic drop
DROP STORAGE LIFECYCLE POLICY my_slp;

-- IF EXISTS
DROP STORAGE LIFECYCLE POLICY IF EXISTS my_db.my_schema.my_slp;
