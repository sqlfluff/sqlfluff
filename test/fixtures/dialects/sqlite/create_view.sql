CREATE TEMPORARY VIEW IF NOT EXISTS temp_table AS
SELECT * FROM tab
WHERE col = 'value';


CREATE VIEW Test.Data (id, name, age)
AS
SELECT id, name, age
FROM temp_table
WHERE age > 18
AND name = 'John';
