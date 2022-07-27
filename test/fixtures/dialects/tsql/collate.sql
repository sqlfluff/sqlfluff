-- `COLLATE` in JOIN condition
SELECT table1.col
FROM table1
INNER JOIN table2
    ON table1.col = table2.col COLLATE Latin1_GENERAL_CS_AS;

-- `COLLATE` in ORDER BY clause
SELECT col
FROM my_table
ORDER BY col COLLATE Latin1_General_CS_AS_KS_WS DESC;

-- `COLLATE` in SELECT
SELECT col COLLATE Latin1_General_CS_AS_KS_WS
FROM my_table;
