SELECT a, b, count(*)
FROM t
GROUP BY a, b WITH ROLLUP;

SELECT a, b, count(*)
FROM t
GROUP BY a, b WITH CUBE;
