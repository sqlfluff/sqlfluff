UPDATE table1
SET a = CASE WHEN t2.column = 'T' THEN TRUE
             WHEN t2.column = 'F' THEN FALSE
             ELSE NULL
        END
FROM table2 t2;
