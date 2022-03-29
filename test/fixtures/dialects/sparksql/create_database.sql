-- Create database with all optional syntax
CREATE DATABASE IF NOT EXISTS database_name
COMMENT "database_comment"
LOCATION "root/database_directory"
WITH DBPROPERTIES ( "property_name" = "property_value");

-- Create schema with all optional syntax
CREATE SCHEMA IF NOT EXISTS database_name
COMMENT "database_comment"
LOCATION "root/database_directory"
WITH DBPROPERTIES ( "property_name" = "property_value" );

-- Create database `customer_db`.
CREATE DATABASE customer_db;

-- Create database `customer_db` only if database with same name doesn't exist.
CREATE DATABASE IF NOT EXISTS customer_db;

-- `Comments`,`Specific Location` and `Database properties`.
CREATE DATABASE IF NOT EXISTS customer_db
COMMENT 'This is customer database' LOCATION '/user'
WITH DBPROPERTIES ("ID" = "001", "Name" = 'John');

-- Create `inventory_db` Database
CREATE DATABASE inventory_db
COMMENT 'This database is used to maintain Inventory';
