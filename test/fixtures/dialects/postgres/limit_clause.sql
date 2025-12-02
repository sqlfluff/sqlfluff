SELECT col_a
FROM test_table
LIMIT 2 * 5 * 10 OFFSET (5 + 10);


SELECT col_a
FROM test_table
LIMIT (10 / 10) OFFSET 10 - 5;


SELECT col_a
FROM test_table
LIMIT 100;


SELECT col_a
FROM test_table
LIMIT ALL;
