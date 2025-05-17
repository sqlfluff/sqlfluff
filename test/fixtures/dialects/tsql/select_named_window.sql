SELECT ROW_NUMBER() OVER win AS [Row Number],
    p.LastName,
    s.SalesYTD,
    a.PostalCode
FROM Sales.SalesPerson AS s
INNER JOIN Person.Person AS p
    ON s.BusinessEntityID = p.BusinessEntityID
INNER JOIN Person.Address AS a
    ON a.AddressID = p.BusinessEntityID
WHERE TerritoryID IS NOT NULL
    AND SalesYTD <> 0
WINDOW win AS
    (
        PARTITION BY PostalCode ORDER BY SalesYTD DESC
    )
ORDER BY PostalCode;

SELECT SalesOrderID,
    ProductID,
    OrderQty,
    SUM(OrderQty) OVER win AS [Total],
    AVG(OrderQty) OVER win AS [Avg],
    COUNT(OrderQty) OVER win AS [Count],
    MIN(OrderQty) OVER win AS [Min],
    MAX(OrderQty) OVER win AS [Max]
FROM Sales.SalesOrderDetail
WHERE SalesOrderID IN (43659, 43664)
WINDOW win AS (PARTITION BY SalesOrderID);

SELECT SalesOrderID AS OrderNumber,
    ProductID,
    OrderQty AS Qty,
    SUM(OrderQty) OVER win AS Total,
    AVG(OrderQty) OVER (win PARTITION BY SalesOrderID) AS Avg,
    COUNT(OrderQty) OVER (
        win ROWS BETWEEN UNBOUNDED PRECEDING
            AND 1 FOLLOWING
        ) AS Count
FROM Sales.SalesOrderDetail
WHERE SalesOrderID IN (43659, 43664)
    AND ProductID LIKE '71%'
WINDOW win AS
    (
        ORDER BY SalesOrderID, ProductID
    );

SELECT SalesOrderID AS OrderNumber, ProductID,
    OrderQty AS Qty,
    SUM(OrderQty) OVER win2 AS Total,
    AVG(OrderQty) OVER win1 AS Avg
FROM Sales.SalesOrderDetail
WHERE SalesOrderID IN(43659,43664) AND
    ProductID LIKE '71%'
WINDOW win1 AS (win3),
    win2 AS (ORDER BY SalesOrderID, ProductID),
    win3 AS (win2 PARTITION BY SalesOrderID);

select row_number() over win as x
from information_schema.tables
window win as (order by table_name)
;
