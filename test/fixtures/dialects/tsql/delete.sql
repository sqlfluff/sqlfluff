DELETE FROM Sales.SalesPersonQuotaHistory;
GO

DELETE FROM Production.ProductCostHistory
WHERE StandardCost > 1000.00;
GO

DELETE Production.ProductCostHistory
WHERE StandardCost BETWEEN 12.00 AND 14.00
      AND EndDate IS NULL;
PRINT 'Number of rows deleted is ' + CAST(@@ROWCOUNT as char(3));
GO

DECLARE complex_cursor CURSOR FOR
    SELECT a.BusinessEntityID
    FROM HumanResources.EmployeePayHistory AS a
    WHERE RateChangeDate <>
         (SELECT MAX(RateChangeDate)
          FROM HumanResources.EmployeePayHistory AS b
          WHERE a.BusinessEntityID = b.BusinessEntityID) ;
OPEN complex_cursor;
FETCH FROM complex_cursor;
DELETE FROM HumanResources.EmployeePayHistory
WHERE CURRENT OF complex_cursor;
CLOSE complex_cursor;
DEALLOCATE complex_cursor;
GO

-- SQL-2003 Standard subquery

DELETE FROM Sales.SalesPersonQuotaHistory
WHERE BusinessEntityID IN
    (SELECT BusinessEntityID
     FROM Sales.SalesPerson
     WHERE SalesYTD > 2500000.00);
GO

-- Transact-SQL extension

DELETE FROM Sales.SalesPersonQuotaHistory
FROM Sales.SalesPersonQuotaHistory AS spqh
INNER JOIN Sales.SalesPerson AS sp
ON spqh.BusinessEntityID = sp.BusinessEntityID
WHERE sp.SalesYTD > 2500000.00;
GO

-- No need to mention target table more than once.

DELETE spqh
  FROM
        Sales.SalesPersonQuotaHistory AS spqh
    INNER JOIN Sales.SalesPerson AS sp
        ON spqh.BusinessEntityID = sp.BusinessEntityID
  WHERE  sp.SalesYTD > 2500000.00;

DELETE TOP (20)
FROM Purchasing.PurchaseOrderDetail
WHERE DueDate < '20020701';
GO

DELETE FROM Purchasing.PurchaseOrderDetail
WHERE PurchaseOrderDetailID IN
   (SELECT TOP 10 PurchaseOrderDetailID
    FROM Purchasing.PurchaseOrderDetail
    ORDER BY DueDate ASC);
GO

-- Specify the remote data source using a four-part name
-- in the form linked_server.catalog.schema.object.

DELETE MyLinkServer.AdventureWorks2012.HumanResources.Department
WHERE DepartmentID > 16;
GO

DELETE OPENQUERY (MyLinkServer, 'SELECT Name, GroupName
FROM AdventureWorks2012.HumanResources.Department
WHERE DepartmentID = 18');
GO

DELETE OPENROWSET('SQLNCLI', 'Server=Seattle1;Trusted_Connection=yes;', Department)
GO

DELETE FROM OPENDATASOURCE('SQLNCLI',
    'Data Source= <server_name>; Integrated Security=SSPI')
    .AdventureWorks2012.HumanResources.Department
WHERE DepartmentID = 17;

DELETE Sales.ShoppingCartItem
OUTPUT DELETED.*
WHERE ShoppingCartID = 20621;

DECLARE @MyTableVar table (
    ProductID int NOT NULL,
    ProductName nvarchar(50)NOT NULL,
    ProductModelID int NOT NULL,
    PhotoID int NOT NULL);

DELETE Production.ProductProductPhoto
OUTPUT DELETED.ProductID,
       p.Name,
       p.ProductModelID,
       DELETED.ProductPhotoID
    INTO @MyTableVar
FROM Production.ProductProductPhoto AS ph
JOIN Production.Product as p
    ON ph.ProductID = p.ProductID
    WHERE p.ProductModelID BETWEEN 120 and 130;
