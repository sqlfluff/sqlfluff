SELECT a, b, count(*)
FROM t
GROUP BY a, b
GROUPING SETS ((a, b), (a), ())
HAVING count(*) > 1;

SELECT a, count(*)
FROM t
GROUP BY a
GROUPING SETS ((a), ());
