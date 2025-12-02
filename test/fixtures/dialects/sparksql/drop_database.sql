-- Drop DATABASE with all optional syntax
DROP DATABASE IF EXISTS dbname RESTRICT;
DROP DATABASE IF EXISTS dbname CASCADE;

-- Drop the database and it's tables
DROP DATABASE inventory_db CASCADE;

-- Drop the database using IF EXISTS
DROP DATABASE IF EXISTS inventory_db CASCADE;
