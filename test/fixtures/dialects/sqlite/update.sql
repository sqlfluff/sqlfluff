UPDATE table_name SET column1 = value1, column2 = value2 WHERE a=1;

UPDATE table_name SET column1 = value1, column2 = value2 WHERE a=1 RETURNING *;

UPDATE table_name SET column1 = value1, column2 = value2 WHERE a=1 RETURNING id foo, id_2 AS bar;
