SELECT *, col1, col2, my_table.col1, my_table.* FROM my_table;

SELECT DISTINCT * FROM my_table;

SELECT DISTINCT col1 FROM my_table;

SELECT ALL my_table.* FROM my_table;

SELECT TOP 1 * FROM my_table;

SELECT TOP 2 col1 FROM my_table;

SELECT TOP 3 col1, my_table.* FROM my_table;

SELECT ALL TOP 10 col1 FROM my_table;

SELECT DISTINCT TOP 20 my_table.col1 FROM my_table;

SELECT DISTINCT TOP 30 * FROM my_table;

SELECT DISTINCT TOP 40 col1, my_table.* FROM my_table;
