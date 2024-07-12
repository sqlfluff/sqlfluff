SELECT *
FROM Sales.Customer AS c
INNER JOIN Sales.CustomerAddress AS ca ON c.CustomerID = ca.CustomerID
WHERE TerritoryID = 5
OPTION (MERGE JOIN);
GO

CREATE PROCEDURE dbo.RetrievePersonAddress
@city_name NVARCHAR(30),
 @postal_code NVARCHAR(15)
AS
SELECT * FROM Person.Address
WHERE City = @city_name AND PostalCode = @postal_code
OPTION ( OPTIMIZE FOR (@city_name = 'Seattle', @postal_code UNKNOWN) );
GO

--Creates an infinite loop
WITH cte (CustomerID, PersonID, StoreID) AS
(
    SELECT CustomerID, PersonID, StoreID
    FROM Sales.Customer
    WHERE PersonID IS NOT NULL
  UNION ALL
    SELECT cte.CustomerID, cte.PersonID, cte.StoreID
    FROM cte
    JOIN  Sales.Customer AS e
        ON cte.PersonID = e.CustomerID
)
--Uses MAXRECURSION to limit the recursive levels to 2
SELECT CustomerID, PersonID, StoreID
FROM cte
OPTION (MAXRECURSION 2);
GO

SELECT *
FROM HumanResources.Employee AS e1
UNION
SELECT *
FROM HumanResources.Employee AS e2
OPTION (MERGE UNION);
GO

SELECT ProductID, OrderQty, SUM(LineTotal) AS Total
FROM Sales.SalesOrderDetail
WHERE UnitPrice < 5
GROUP BY ProductID, OrderQty
ORDER BY ProductID, OrderQty
OPTION (HASH GROUP, FAST 10);
GO

SELECT ProductID, OrderQty, SUM(LineTotal) AS Total
FROM Sales.SalesOrderDetail
WHERE UnitPrice < 5
GROUP BY ProductID, OrderQty
ORDER BY ProductID, OrderQty
OPTION (MAXDOP 2);
GO

SELECT * FROM Person.Address
WHERE City = 'SEATTLE' AND PostalCode = 98104
OPTION (RECOMPILE, USE HINT ('ASSUME_MIN_SELECTIVITY_FOR_FILTER_ESTIMATES', 'DISABLE_PARAMETER_SNIFFING'));
GO

SELECT * FROM Person.Address
WHERE City = 'SEATTLE' AND PostalCode = 98104
OPTION (QUERYTRACEON 4199);
GO

SELECT * FROM Person.Address
WHERE City = 'SEATTLE' AND PostalCode = 98104
OPTION  (QUERYTRACEON 4199, QUERYTRACEON 4137);
GO

UPDATE Production.Product
WITH (TABLOCK)
SET ListPrice = ListPrice * 1.10
WHERE ProductNumber LIKE 'BK-%';
GO

SELECT *
FROM Sales.SalesOrderHeader AS h
INNER JOIN Sales.SalesOrderDetail AS d WITH (FORCESEEK)
    ON h.SalesOrderID = d.SalesOrderID
WHERE h.TotalDue > 100
AND (d.OrderQty > 5 OR d.LineTotal < 1000.00);
GO

SELECT h.SalesOrderID, h.TotalDue, d.OrderQty
FROM Sales.SalesOrderHeader AS h
    INNER JOIN Sales.SalesOrderDetail AS d
    WITH (FORCESEEK (PK_SalesOrderDetail_SalesOrderID_SalesOrderDetailID (SalesOrderID)))
    ON h.SalesOrderID = d.SalesOrderID
WHERE h.TotalDue > 100
AND (d.OrderQty > 5 OR d.LineTotal < 1000.00);
GO

SELECT h.SalesOrderID, h.TotalDue, d.OrderQty
FROM Sales.SalesOrderHeader AS h
    INNER JOIN Sales.SalesOrderDetail AS d
    WITH (FORCESCAN)
    ON h.SalesOrderID = d.SalesOrderID
WHERE h.TotalDue > 100
AND (d.OrderQty > 5 OR d.LineTotal < 1000.00);
GO

SELECT ID
FROM dbo.tableX WITH(NOLOCK)
GO

SELECT ID
FROM dbo.tableX (NOLOCK)
GO
