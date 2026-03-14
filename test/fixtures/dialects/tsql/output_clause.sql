-- OUTPUT clause tests
-- https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql

-- Example 1: OUTPUT with DELETE (no INTO) - wildcard
DELETE Sales.ShoppingCartItem
OUTPUT DELETED.*
WHERE ShoppingCartID = 20621;
GO

-- Example 2: OUTPUT with DELETE - specific columns
DELETE Sales.ShoppingCartItem
OUTPUT DELETED.ProductID, DELETED.Quantity
WHERE ShoppingCartID = 20621;
GO

-- Example 3: OUTPUT with DELETE - column with alias
DELETE Sales.ShoppingCartItem
OUTPUT DELETED.ProductID AS RemovedProductID
WHERE ShoppingCartID = 20621;
GO

-- Example 4: OUTPUT INTO with DELETE
DECLARE @DeletedRows TABLE (
    ProductID INT,
    Quantity INT
);

DELETE Sales.ShoppingCartItem
OUTPUT DELETED.ProductID, DELETED.Quantity
INTO @DeletedRows
WHERE ShoppingCartID = 20621;
GO

-- Example 5: OUTPUT INTO with table variable and column list
DECLARE @MyTableVar TABLE (
    NewScrapReasonID SMALLINT,
    Name VARCHAR(50),
    ModifiedDate DATETIME
);

INSERT Production.ScrapReason
OUTPUT INSERTED.ScrapReasonID, INSERTED.Name, INSERTED.ModifiedDate
INTO @MyTableVar
VALUES (N'Operator error', GETDATE());
GO

-- Example 6: OUTPUT with INSERT - no INTO
INSERT Production.ScrapReason
OUTPUT INSERTED.ScrapReasonID, INSERTED.Name
VALUES (N'Operator error', GETDATE());
GO

-- Example 7: OUTPUT with UPDATE - DELETED and INSERTED
DECLARE @UpdatedRows TABLE (
    EmpID INT NOT NULL,
    OldVacationHours INT,
    NewVacationHours INT
);

UPDATE HumanResources.Employee
SET VacationHours = VacationHours * 1.25
OUTPUT INSERTED.BusinessEntityID,
       DELETED.VacationHours,
       INSERTED.VacationHours
INTO @UpdatedRows
WHERE BusinessEntityID < 10;
GO

-- Example 8: OUTPUT with expression
UPDATE HumanResources.Employee
SET VacationHours = VacationHours * 1.25
OUTPUT INSERTED.BusinessEntityID,
       DELETED.VacationHours AS OldValue,
       INSERTED.VacationHours AS NewValue,
       INSERTED.VacationHours - DELETED.VacationHours AS Difference
WHERE BusinessEntityID < 10;
GO

-- Example 9: OUTPUT with from_table_name in UPDATE
DECLARE @MyTestVar TABLE (
    OldScrapReasonID INT,
    NewScrapReasonID INT,
    WorkOrderID INT,
    ProductID INT,
    ProductName NVARCHAR(50)
);

UPDATE Production.WorkOrder
SET ScrapReasonID = 4
OUTPUT DELETED.ScrapReasonID,
       INSERTED.ScrapReasonID,
       INSERTED.WorkOrderID,
       INSERTED.ProductID,
       p.Name
INTO @MyTestVar
FROM Production.WorkOrder AS wo
INNER JOIN Production.Product AS p
    ON wo.ProductID = p.ProductID
WHERE wo.ScrapReasonID = 16;
GO

-- Example 10: OUTPUT with MERGE and $ACTION
DECLARE @SummaryOfChanges TABLE (
    ChangeType NVARCHAR(10),
    ProductID INT
);

MERGE Production.ProductInventory AS target
USING (SELECT ProductID, SUM(OrderQty) AS TotalQty
       FROM Sales.SalesOrderDetail
       GROUP BY ProductID) AS source
ON target.ProductID = source.ProductID
WHEN MATCHED AND target.Quantity - source.TotalQty <= 0 THEN
    DELETE
WHEN MATCHED THEN
    UPDATE SET target.Quantity = target.Quantity - source.TotalQty
OUTPUT $ACTION, DELETED.ProductID
INTO @SummaryOfChanges;
GO

-- Example 11: OUTPUT without INTO in MERGE
MERGE Production.ProductInventory AS target
USING (SELECT ProductID, SUM(OrderQty) AS TotalQty
       FROM Sales.SalesOrderDetail
       GROUP BY ProductID) AS source
ON target.ProductID = source.ProductID
WHEN MATCHED THEN
    UPDATE SET target.Quantity = target.Quantity - source.TotalQty
OUTPUT $ACTION, INSERTED.ProductID, INSERTED.Quantity;
GO

-- Example 12: OUTPUT with table reference (real table, not variable)
CREATE TABLE #OutputTable (
    ProductID INT,
    DeletedQuantity INT
);

DELETE Sales.ShoppingCartItem
OUTPUT DELETED.ProductID, DELETED.Quantity
INTO #OutputTable
WHERE ShoppingCartID = 20621;
GO

-- Example 13: OUTPUT with INTO and column list
DECLARE @Results TABLE (
    ProdID INT,
    Qty INT
);

DELETE Sales.ShoppingCartItem
OUTPUT DELETED.ProductID, DELETED.Quantity
INTO @Results (ProdID, Qty)
WHERE ShoppingCartID = 20621;
GO

-- Example 14: Multiple columns in OUTPUT with various expressions
UPDATE Production.Product
SET ListPrice = ListPrice * 1.1
OUTPUT INSERTED.ProductID,
       DELETED.ListPrice,
       INSERTED.ListPrice,
       GETDATE() AS UpdateDate,
       SYSTEM_USER AS UpdatedBy
WHERE ProductID = 680;
GO
