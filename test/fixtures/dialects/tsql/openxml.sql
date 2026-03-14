-- https://learn.microsoft.com/en-us/sql/t-sql/functions/openxml-transact-sql
-- https://learn.microsoft.com/en-us/sql/relational-databases/xml/specify-metaproperties-in-openxml

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
FROM OPENXML(@idoc, '/ROOT/Customer/Order/OrderDetail')
WITH (
    OrderID INT '../@OrderID',
    CustomerID VARCHAR(10) '../@CustomerID',
    OrderDate DATETIME '../@OrderDate',
    ProdID INT '@ProductID',
    Qty INT '@Quantity'
);

-- Specifying TableName in the WITH clause
SELECT *
FROM OPENXML (@docHandle, '/root/Customer/Order', 1)
WITH T1;

-- metaproperties example
SELECT *
FROM OPENXML (@idoc, '/root/Customer/Order', 9)
WITH (id int '@mp:id',
    oid char(5),
    date datetime,
    amount real,
    parentIDNo int '@mp:parentid',
    parentLocalName varchar(40) '@mp:parentlocalname');
