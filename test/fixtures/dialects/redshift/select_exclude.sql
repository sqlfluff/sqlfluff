SELECT * EXCLUDE col1 FROM table1;

SELECT * EXCLUDE col1, col2 FROM table1;

SELECT * EXCLUDE (col1) FROM table1;

SELECT * EXCLUDE (col1, col2) FROM table1;

SELECT *, NULL AS example EXCLUDE (col1, col2) FROM table1;
