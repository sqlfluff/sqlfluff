SELECT * EXCLUDE col1 FROM table1;

SELECT * EXCLUDE col1, col2 FROM table1;

SELECT * EXCLUDE (col1) FROM table1;

SELECT * EXCLUDE (col1, col2) FROM table1;

SELECT *, NULL AS example EXCLUDE (col1, col2) FROM table1;

SELECT *, 1 EXCLUDE (col1) FROM table1;

SELECT *, a EXCLUDE x FROM tbl;

SELECT col1, col2, col3 EXCLUDE (col2) FROM table1;

SELECT a.col1, b.* EXCLUDE (col2, col3) FROM table1 AS a, table2 AS b;

SELECT EXCLUDE FROM table1;

SELECT EXCLUDE, col1 FROM table1;

SELECT "EXCLUDE" FROM table1;

SELECT EXCLUDE(col1) FROM table1;

SELECT schema.EXCLUDE(col1) FROM table1;

SELECT 1 AS EXCLUDE FROM table1;

SELECT a, b, FROM table1;
