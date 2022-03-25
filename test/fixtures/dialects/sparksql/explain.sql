EXPLAIN SELECT
    a,
    b
FROM person;

EXPLAIN SELECT TRANSFORM (zip_code, name, age)
    USING 'cat' AS (a, b, c)
FROM person
WHERE zip_code > 94511;

EXPLAIN ALTER DATABASE inventory SET DBPROPERTIES (
    'Edited-by' = 'John'
);

EXPLAIN ALTER TABLE student RENAME TO studentinfo;

EXPLAIN ALTER VIEW view_identifier RENAME TO view_identifier;

EXPLAIN CREATE DATABASE IF NOT EXISTS database_name
COMMENT "database_comment"
LOCATION "root/database_directory"
WITH DBPROPERTIES ( "property_name" = "property_value");

EXPLAIN CREATE OR REPLACE TEMPORARY FUNCTION IF NOT EXISTS
function_name AS "class_name" USING FILE "resource_locations";

EXPLAIN CREATE TABLE student (id INT, student_name STRING, age INT) USING CSV;

EXPLAIN
CREATE TABLE student (id INT, student_name STRING, age INT)
STORED AS ORC;

EXPLAIN CREATE TABLE student_dupli LIKE student
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('owner' = 'xxxx');

EXPLAIN
CREATE VIEW experienced_employee_extended
AS SELECT a
FROM experienced_employee;

EXPLAIN DROP DATABASE IF EXISTS dbname;

EXPLAIN DROP FUNCTION test_avg;

EXPLAIN USE database_name;

EXPLAIN TRUNCATE TABLE student PARTITION(age = 10);

EXPLAIN MSCK REPAIR TABLE table_identifier ADD PARTITIONS;

EXPLAIN REFRESH TABLE tbl1;

EXPLAIN REFRESH FUNCTION func1;

EXPLAIN LOAD DATA LOCAL INPATH '/user/hive/warehouse/students'
OVERWRITE INTO TABLE test_load;

EXPLAIN INSERT INTO TABLE students VALUES
('Amy Smith', '123 Park Ave, San Jose', 111111);

EXPLAIN DROP VIEW IF EXISTS view_identifier;
