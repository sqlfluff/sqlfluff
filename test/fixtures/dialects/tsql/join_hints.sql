-- HASH JOIN
SELECT table1.col
FROM table1
INNER HASH JOIN table2
    ON table1.col = table2.col;

-- OUTER MERGE JOIN
SELECT table1.col
FROM table1
FULL OUTER MERGE JOIN table2
    ON table1.col = table2.col;

-- LEFT LOOP JOIN
SELECT table1.col
FROM table1
LEFT LOOP JOIN table2
    ON table1.col = table2.col;
