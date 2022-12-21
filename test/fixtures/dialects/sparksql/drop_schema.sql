-- Drop schema with all optional syntax
DROP SCHEMA IF EXISTS dbname RESTRICT;
DROP SCHEMA IF EXISTS dbname CASCADE;

-- Drop the database and it's tables
DROP SCHEMA inventory_db CASCADE;

-- Drop the database using IF EXISTS
DROP SCHEMA IF EXISTS inventory_db CASCADE;
