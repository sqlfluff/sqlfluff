SELECT DISTINCT
    field_1
FROM table_1
EXCEPT (
    SELECT DISTINCT field_1
    FROM table_2
);

SELECT field_1
FROM table_1
INTERSECT (
    SELECT field_1
    FROM table_2
);

SELECT field_1
FROM table_1
EXCEPT ALL (
    SELECT field_1
    FROM table_2
);

SELECT field_1
FROM table_1
UNION (
    SELECT field_1
    FROM table_2
);
