-- Create Table Like with all optional syntax
CREATE TABLE IF NOT EXISTS table_identifier LIKE source_table_identifier
USING PARQUET
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS PARQUET
TBLPROPERTIES ( "key1" = "val1", "key2" = "val2")
LOCATION "path/to/files";

-- Create table using an existing table
CREATE TABLE student_dupli LIKE student;

-- Create table like using a data source
CREATE TABLE student_dupli LIKE student USING CSV;

-- Table is created as external table at the location specified
CREATE TABLE student_dupli LIKE student LOCATION '/root1/home';

-- Create table like using a rowformat
CREATE TABLE student_dupli LIKE student
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('owner' = 'xxxx');
