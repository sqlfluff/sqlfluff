-- Test GROUP BY with GROUPING SETS, CUBE, ROLLUP, and empty sets in T-SQL
-- Issue #8738: T-SQL: GROUP BY GROUPING SETS with more than one set fails to parse

SELECT CustomerType, ProductLine, COUNT(*) AS OrderCount
FROM dbo.Orders
GROUP BY GROUPING SETS ((CustomerType, ProductLine), (CustomerType), ());

SELECT CustomerType, ProductLine, COUNT(*) AS OrderCount
FROM dbo.Orders
GROUP BY GROUPING SETS ((CustomerType, ProductLine));

SELECT col1, col2, COUNT(*) AS cnt
FROM dbo.Orders
GROUP BY col1, GROUPING SETS ((col2), ());

SELECT col1, col2, COUNT(*) AS cnt
FROM dbo.Orders
GROUP BY CUBE (col1, col2);

SELECT col1, col2, COUNT(*) AS cnt
FROM dbo.Orders
GROUP BY ROLLUP (col1, col2);

SELECT COUNT(*) AS total
FROM dbo.Orders
GROUP BY ();

SELECT col1, col2, COUNT(*) AS cnt
FROM dbo.Orders
GROUP BY ALL col1, col2;
