-- https://duckdb.org/docs/stable/sql/expressions/in
SELECT 'Math' IN ('CS', 'Math');
SELECT 'Math' IN ('CS', 'Math',);
SELECT 42 IN (SELECT unnest([32, 42, 52]) AS x);
SELECT 'Hello' IN 'Hello World';
SELECT 1 IN [1,2,3];
SELECT 17 in [x, y, z,] from t;
SELECT x NOT IN y;
select 17 in (x,y,z,) from t;
-- This test case doesn't work yet, MAP literals are not parsed.
-- https://duckdb.org/docs/stable/sql/data_types/map
-- SELECT 'key1' IN MAP {'key1': 50, 'key2': 75};
