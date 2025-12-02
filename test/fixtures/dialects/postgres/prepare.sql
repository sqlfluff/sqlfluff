PREPARE select_statement AS
SELECT * FROM table1;

PREPARE insert_statement AS
INSERT INTO table1 (col1, col2) VALUES (1, 'foo');

PREPARE update_statement AS
UPDATE table1 SET col2 = 'bar' WHERE col1 = 1;

PREPARE delete_statement AS
DELETE FROM table1 WHERE col1 = 1;

PREPARE values_statement AS
VALUES (1, 'foo');

PREPARE merge_statement AS
MERGE INTO table1 USING table2 ON (table1.col1 = table2.col1)
WHEN MATCHED THEN
UPDATE SET col1 = table2.col1, col2 = table2.col2
WHEN NOT MATCHED THEN
INSERT (col1, col2) VALUES (table2.col1, table2.col2);

PREPARE parametrized_statement_1 (int) AS
VALUES ($1);

PREPARE parametrized_statement_2 (int, character(3)) AS
VALUES ($1, $2);
