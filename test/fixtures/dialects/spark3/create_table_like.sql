-- Create Table Like with all optional syntax
CREATE TABLE IF NOT EXISTS table_identifier LIKE source_table_identifier
    USING PARQUET
    ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
    STORED AS PARQUET
    TBLPROPERTIES ( "key1" = "val1", "key2" = "val2")
    LOCATION "path/to/files"

-- Create table using an existing table
CREATE TABLE Student_Dupli like Student;

-- Create table like using a data source
CREATE TABLE Student_Dupli like Student USING CSV;

-- Table is created as external table at the location specified
CREATE TABLE Student_Dupli like Student location  '/root1/home';

-- Create table like using a rowformat
CREATE TABLE Student_Dupli like Student
    ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    TBLPROPERTIES ('owner'='xxxx');
