ALTER CATALOG cat2 SET ('default-database' = 'db');

ALTER CATALOG cat2 RESET ('default-database');

ALTER CATALOG cat2 COMMENT 'comment for catalog ''cat2''';

ALTER DATABASE my_cat.my_db SET ('key1' = 'val1', 'key2' = 'val2');

ALTER FUNCTION my_func AS 'com.example.NewUdf';

ALTER TEMPORARY FUNCTION IF EXISTS my_db.`my-func` AS 'com.example.NewUdf' LANGUAGE JAVA;

ALTER TEMPORARY SYSTEM FUNCTION IF EXISTS my_func AS 'pyflink.udf.fn' LANGUAGE PYTHON;

ALTER VIEW my_view RENAME TO new_view;

ALTER VIEW my_view AS
SELECT
    id,
    name
FROM my_table;
