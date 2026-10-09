-- A closing bracket is a code boundary: a following keyword starts
-- the next clause even without whitespace between them.
SELECT (a)FROM t;

SELECT (a)WHERE a > 1;

SELECT (a)ORDER BY a;

SELECT (a)LIMIT 1;

SELECT count(DISTINCT sk)FROM t;
