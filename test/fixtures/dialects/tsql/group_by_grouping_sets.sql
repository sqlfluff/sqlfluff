SELECT CustomerType, ProductLine, COUNT(*) AS OrderCount
FROM dbo.Orders
GROUP BY GROUPING SETS ((CustomerType, ProductLine), (CustomerType), ());

SELECT country, city, street_name, sum(income)
FROM addresses
GROUP BY country, ROLLUP (city, street_name);

SELECT a, b, c, count(*)
FROM t
GROUP BY CUBE (a), ROLLUP (b, c);

SELECT count(*)
FROM addresses
GROUP BY ();

SELECT a, count(*)
FROM t
GROUP BY ALL a;

SELECT a, count(*)
FROM t
GROUP BY a WITH CUBE;

SELECT a, count(*)
FROM t
GROUP BY a, GROUPING SETS (b, ());
