-- MySQL GROUP BY ... WITH ROLLUP modifier
-- https://dev.mysql.com/doc/refman/8.0/en/group-by-modifiers.html

SELECT a, SUM(b) FROM t GROUP BY a WITH ROLLUP;

SELECT a, b, SUM(c) FROM t GROUP BY a, b WITH ROLLUP;

SELECT a, SUM(b) FROM t GROUP BY 1 WITH ROLLUP HAVING SUM(b) > 10;

SELECT a, SUM(b) FROM t GROUP BY a WITH ROLLUP ORDER BY a;
