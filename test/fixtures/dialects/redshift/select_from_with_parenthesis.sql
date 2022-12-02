-- https://github.com/sqlfluff/sqlfluff/issues/3955

SELECT table_1.id FROM (table_1);

SELECT table_1.id FROM (table_1 INNER JOIN table_2 ON table_2.id = table_1.id);
