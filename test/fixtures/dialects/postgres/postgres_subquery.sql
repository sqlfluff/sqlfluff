INSERT INTO target_table (target_column)
SELECT table1.column1
FROM table1
INNER JOIN (
    SELECT table2.join_column
    FROM table2
) AS temp3
ON table1.join_column = temp3.join_column
