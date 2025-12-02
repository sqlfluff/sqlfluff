-- Create view basic syntax
CREATE VIEW experienced_employee_extended AS SELECT * from experienced_employee ;

-- Create VIEW with all optional syntax
CREATE OR REPLACE GLOBAL TEMPORARY VIEW IF NOT EXISTS experienced_employee
(ID COMMENT 'Unique identification number', Name)
COMMENT 'View for experienced employees'
TBLPROPERTIES ( "key1" = "val1", "key2" = "val2" )
AS SELECT ID, Name from temp2 ;

-- Created a temporary function with TEMP.
CREATE TEMP VIEW experienced_employee_temp AS
SELECT * from experienced_employee limit 2 ;

-- Replace the implementation of `simple_udf`
CREATE OR REPLACE VIEW experienced_employee_rep AS
SELECT * from experienced_employee limit 2 ;

CREATE TEMPORARY VIEW pulse_article_search_data
    USING org.apache.spark.sql.jdbc
    OPTIONS (
  url "jdbc:postgresql:dbserver",
  dbtable "schema.tablename",
  user 'username',
  password 'password'
)
