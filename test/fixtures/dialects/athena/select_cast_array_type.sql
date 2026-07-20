-- Athena uses Trino data type names in DML, so an array type is ARRAY(type).
-- https://github.com/sqlfluff/sqlfluff/issues/4193
SELECT CAST(col1 AS ARRAY(VARCHAR)) AS c1;

SELECT CAST(col1 AS ARRAY(ROW(id VARCHAR))) AS c1;

SELECT CAST(
    ROW(ARRAY[CAST(ROW('') AS ROW(id VARCHAR))], CAST(ROW('') AS ROW(id VARCHAR)), 'Approved')
    AS ROW(approvers ARRAY(ROW(id VARCHAR)), performer ROW(id VARCHAR), approvalstatus VARCHAR)
) AS test;

-- DDL still uses the Hive spelling.
CREATE EXTERNAL TABLE array_table (c1 ARRAY<INTEGER>) LOCATION 's3://bucket/path/';
