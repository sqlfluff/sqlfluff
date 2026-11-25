-- https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-sensitivity-classification-transact-sql
DROP SENSITIVITY CLASSIFICATION FROM dbo.sales.price;

DROP SENSITIVITY CLASSIFICATION FROM
    dbo.sales.price, dbo.sales.discount, [SalesLT].[Customer].[Phone];
