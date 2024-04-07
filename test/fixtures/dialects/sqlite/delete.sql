DELETE FROM table_name
WHERE a > 0;

DELETE FROM table_name
WHERE a > 0
RETURNING *
;

DELETE FROM table_name
WHERE a > 0
RETURNING *, id
;

DELETE FROM table_name
WHERE a > 0
RETURNING id foo, id_2 AS bar
;
