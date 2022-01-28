SELECT *
FROM table1 natural -- this should parse as an alias as TSQL does not have NATURAL joins
JOIN table2;

SELECT *
FROM table1 natural -- this should parse as an alias as TSQL does not have NATURAL joins
INNER JOIN table2;
