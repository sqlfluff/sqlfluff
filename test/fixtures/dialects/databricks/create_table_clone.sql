-- Deep clone (default)
CREATE TABLE my_catalog.my_schema.target_table
CLONE my_catalog.my_schema.source_table;

-- Explicit deep clone
CREATE TABLE target_table
DEEP CLONE source_table;

-- Shallow clone
CREATE TABLE target_table
SHALLOW CLONE source_table;

-- Clone with IF NOT EXISTS
CREATE TABLE IF NOT EXISTS target_table
CLONE source_table;

-- Clone with TBLPROPERTIES
CREATE TABLE target_table
DEEP CLONE source_table
TBLPROPERTIES ('delta.logRetentionDuration' = 'interval 30 days');

-- Clone with LOCATION
CREATE TABLE target_table
SHALLOW CLONE source_table
LOCATION '/mnt/data/target';

-- Clone with both TBLPROPERTIES and LOCATION
CREATE TABLE target_table
DEEP CLONE source_table
TBLPROPERTIES ('somekey' = 'somevalue')
LOCATION '/mnt/data/target';

-- CREATE OR REPLACE TABLE CLONE
CREATE OR REPLACE TABLE target_table
CLONE source_table;

-- REPLACE TABLE CLONE
REPLACE TABLE target_table
SHALLOW CLONE source_table;

-- Create or replace table clone with both TBLPROPERTIES and LOCATION
CREATE OR REPLACE TABLE target_table
DEEP CLONE source_table
TBLPROPERTIES ('somekey' = 'somevalue')
LOCATION '/mnt/data/target';
