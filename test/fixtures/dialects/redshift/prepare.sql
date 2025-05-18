PREPARE select_statement AS
SELECT * FROM table1;

PREPARE insert_statement AS
INSERT INTO table1 (col1, col2) VALUES (1, 'foo');

PREPARE update_statement AS
UPDATE table1 SET col2 = 'bar' WHERE col1 = 1;

PREPARE delete_statement AS
DELETE FROM table1 WHERE col1 = 1;

PREPARE parametrized_statement_1 (int) AS
SELECT ($1);

PREPARE parametrized_statement_2 (int, character(3)) AS
SELECT $1, $2;
