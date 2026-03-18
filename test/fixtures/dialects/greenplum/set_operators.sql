SELECT DISTINCT
    field_1
FROM table_1
EXCEPT (
    SELECT DISTINCT field_1
    FROM table_2
);
