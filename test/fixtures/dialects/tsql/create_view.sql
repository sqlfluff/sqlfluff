CREATE OR ALTER VIEW Sales.SalesPersonPerform
AS
SELECT TOP (100) SalesPersonID, SUM(TotalDue) AS TotalSales
FROM Sales.SalesOrderHeader
WHERE OrderDate > CONVERT(DATETIME, '20001231', 101)
GROUP BY SalesPersonID;

CREATE OR ALTER VIEW Sales.SalesPersonPerform
AS
SELECT TOP (100) SalesPersonID, SUM(TotalDue) AS TotalSales
FROM Sales.SalesOrderHeader
WHERE OrderDate > CONVERT(DATETIME, '20001231', 101)
GROUP BY SalesPersonID;


CREATE VIEW Purchasing.PurchaseOrderReject
WITH SCHEMABINDING
AS
SELECT PurchaseOrderID, ReceivedQty, RejectedQty,
    RejectedQty / ReceivedQty AS RejectRatio, DueDate
FROM Purchasing.PurchaseOrderDetail
WHERE RejectedQty / ReceivedQty > 0
AND DueDate > CONVERT(DATETIME,'20010630',101) ;


CREATE VIEW dbo.SeattleOnly
AS
SELECT p.LastName, p.FirstName, e.JobTitle, a.City, sp.StateProvinceCode
FROM HumanResources.Employee e
INNER JOIN Person.Person p
ON p.BusinessEntityID = e.BusinessEntityID
    INNER JOIN Person.BusinessEntityAddress bea
    ON bea.BusinessEntityID = e.BusinessEntityID
    INNER JOIN Person.Address a
    ON a.AddressID = bea.AddressID
    INNER JOIN Person.StateProvince sp
    ON sp.StateProvinceID = a.StateProvinceID
WHERE a.City = 'Seattle'
WITH CHECK OPTION ;


CREATE VIEW dbo.all_supplier_view
WITH SCHEMABINDING
AS
SELECT supplyID, supplier
  FROM dbo.SUPPLY1
UNION ALL
SELECT supplyID, supplier
  FROM dbo.SUPPLY2
UNION ALL
SELECT supplyID, supplier
  FROM dbo.SUPPLY3
UNION ALL
SELECT supplyID, supplier
  FROM dbo.SUPPLY4;

create view vw_view with schemabinding, view_metadata as select A.ID from A
