-- `CROSS JOIN`
SELECT table1.col, table2.col, table3.other_col
FROM table1
CROSS JOIN table2
    JOIN table3
        ON table1.col = table3.col;
