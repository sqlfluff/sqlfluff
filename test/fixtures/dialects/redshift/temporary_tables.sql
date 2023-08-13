CREATE TEMPORARY TABLE #temp_table AS
SELECT name FROM other_table;

CREATE TABLE #other_temp_table (id int);

COPY #temp_table FROM 's3://mybucket/path'
CREDENTIALS 'aws_access_key_id=SECRET;aws_secret_access_key=ALSO_SECRET'
GZIP;

SELECT * FROM #temp_table;
