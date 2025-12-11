-- https://learn.microsoft.com/en-us/sql/t-sql/functions/openxml-transact-sql?view=sql-server-ver16

SELECT col1
FROM
    OPENXML (@iDoc, N'root/search', 1);

SELECT col1
FROM
    OPENXML (@iDoc, N'root/search', 1)
    WITH (
        CustomerID VARCHAR(10),
        ContactName VARCHAR(20)
    );

SELECT *
FROM OPENXML(@idoc, '/ROOT/Customer/Order/OrderDetail', 2) WITH (
    OrderID INT '../@OrderID',
    CustomerID VARCHAR(10) '../@CustomerID',
    OrderDate DATETIME '../@OrderDate',
    ProdID INT '@ProductID',
    Qty INT '@Quantity'
);
