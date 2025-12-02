PREPARE my_select1 FROM
SELECT * FROM nation;

PREPARE my_select2 FROM
SELECT * FROM "my_database"."my_table" WHERE year = ?;

PREPARE my_select3 FROM
SELECT 'order' FROM orders WHERE productid = ? and quantity < ?;

PREPARE my_insert FROM
INSERT INTO cities_usa (city, state)
SELECT city, state
FROM cities_world
WHERE country = ?;

PREPARE my_unload FROM
UNLOAD (SELECT * FROM table1 WHERE productid < ?)
TO 's3://my_output_bucket/'
WITH (format='PARQUET');

EXECUTE statement_name;
EXECUTE statement_name USING 'value';
EXECUTE statement_name USING 'value', 10;
