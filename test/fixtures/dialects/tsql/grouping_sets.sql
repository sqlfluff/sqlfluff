-- https://github.com/sqlfluff/sqlfluff/issues/8738
SELECT CustomerType, ProductLine, COUNT(*) AS OrderCount
FROM dbo.Orders
GROUP BY GROUPING SETS ((CustomerType, ProductLine), (CustomerType), ());

SELECT CustomerType, ProductLine, COUNT(*) AS OrderCount
FROM dbo.Orders
GROUP BY GROUPING SETS (
    ROLLUP(CustomerType, ProductLine),
    CUBE(CustomerType)
);

SELECT CustomerType, COUNT(*) AS OrderCount
FROM dbo.Orders
GROUP BY ROLLUP (CustomerType, ProductLine);

SELECT CustomerType, COUNT(*) AS OrderCount
FROM dbo.Orders
GROUP BY CUBE (CustomerType);
