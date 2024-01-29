-- Standard IN
SELECT uniq(col1) FROM table1 WHERE col1 IN (SELECT col1 FROM table1 WHERE col2 = 34);
SELECT uniq(col1) FROM table1 WHERE col1 NOT IN (SELECT col1 FROM table1 WHERE col2 = 34);

-- GLOBAL IN
SELECT uniq(col1) FROM table1 WHERE col1 GLOBAL IN (SELECT col1 FROM table1 WHERE col2 = 34);
SELECT uniq(col1) FROM table1 WHERE col1 GLOBAL NOT IN (SELECT col1 FROM table1 WHERE col2 = 34);

-- IN FUNCTION
SELECT uniq(col1) FROM table1 WHERE col1 IN tuple(1, 2);
SELECT uniq(col1) FROM table1 WHERE col1 NOT IN tuple(1, 2);
SELECT uniq(col1) FROM table1 WHERE col1 GLOBAL IN tuple(1, 2);
SELECT uniq(col1) FROM table1 WHERE col1 GLOBAL NOT IN tuple(1, 2);
