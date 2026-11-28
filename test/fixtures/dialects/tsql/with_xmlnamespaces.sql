WITH XMLNAMESPACES ('https://example.com/orders' AS o)
SELECT OrderXml.value('(/o:Order/@Id)[1]', 'INT') AS OrderId
FROM dbo.Orders;
GO

WITH XMLNAMESPACES (DEFAULT 'https://example.com/orders')
SELECT OrderId
FROM dbo.Orders
FOR XML AUTO;
GO

WITH XMLNAMESPACES (
    DEFAULT N'https://example.com/orders',
    N'https://example.com/customers' AS Cust,
    'https://example.com/items' AS [item],
    'https://example.com/products' AS "product"
)
SELECT OrderXml.query('/Order/Cust:Customer') AS Customer
FROM dbo.Orders;
GO

-- Before a common table expression
WITH XMLNAMESPACES ('https://example.com/orders' AS o),
OrderIds AS (
    SELECT OrderXml.value('(/o:Order/@Id)[1]', 'INT') AS OrderId
    FROM dbo.Orders
)

SELECT OrderId
FROM OrderIds;
GO

-- With other statements
WITH XMLNAMESPACES ('https://example.com/orders' AS o)
INSERT INTO dbo.OrderIds (OrderId)
SELECT OrderXml.value('(/o:Order/@Id)[1]', 'INT')
FROM dbo.Orders;
GO

WITH XMLNAMESPACES ('https://example.com/orders' AS o)
DELETE FROM dbo.Orders
WHERE OrderXml.exist('/o:Order/o:Cancelled') = 1;
GO

CREATE VIEW dbo.OrderIdsView
AS
WITH XMLNAMESPACES ('https://example.com/orders' AS o)
SELECT OrderXml.value('(/o:Order/@Id)[1]', 'INT') AS OrderId
FROM dbo.Orders;
GO

DECLARE OrderCursor CURSOR FOR
WITH XMLNAMESPACES ('https://example.com/orders' AS o)
SELECT OrderXml.value('(/o:Order/@Id)[1]', 'INT')
FROM dbo.Orders;
GO
