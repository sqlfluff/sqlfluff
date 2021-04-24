SET var1 = 10;

SET var1 = TRUE;

SET var1 = 'example';

SET var1 = CURRENT_TIMESTAMP;

-- @TODO: Does not work. `pytest dialects_test.py` throws a SQLLexError on this line.
SET var1 = $var2;

SET var1 = TO_DATE('2021-01-01');

SET var1 = (SELECT 10);

SET var1 = (SELECT AVG(col1) FROM table1 WHERE col2 IS NOT NULL LIMIT 1);

SET var1 = (SELECT AVG(col1) FROM table1 WHERE col2 BETWEEN 10 AND 11 LIMIT 10) / 2;
