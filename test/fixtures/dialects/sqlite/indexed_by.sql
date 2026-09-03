-- https://www.sqlite.org/lang_indexedby.html

SELECT * FROM my_table INDEXED BY my_index WHERE a = 1;
SELECT * FROM my_table NOT INDEXED WHERE a = 1;
SELECT * FROM my_table AS t INDEXED BY my_index;
SELECT *
FROM my_table
INNER JOIN other_table INDEXED BY other_index
    ON my_table.id = other_table.id;

DELETE FROM my_table INDEXED BY my_index WHERE a = 1;
DELETE FROM my_table NOT INDEXED;

UPDATE my_table INDEXED BY my_index SET a = 1 WHERE b = 2;
UPDATE my_table AS t NOT INDEXED SET a = 1;
