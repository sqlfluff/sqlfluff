DELETE dbo.Table2
FROM dbo.Table2
    INNER JOIN dbo.Table1
    ON (dbo.Table2.ColA = dbo.Table1.ColA)
    WHERE dboTable2.ColA = 1;

DELETE
FROM dodos WITH(NOLOCK)
OUTPUT age INTO ages

DELETE FROM Table1;

DELETE FROM Table1
WHERE StandardCost > 1000.00;

DELETE FROM Table1
OPTION ( LABEL = N'label1' );

DELETE FROM dbo.FactInternetSales
WHERE ProductKey IN (
    SELECT T1.ProductKey FROM dbo.DimProduct T1
    JOIN dbo.DimProductSubcategory T2
    ON T1.ProductSubcategoryKey = T2.ProductSubcategoryKey
    WHERE T2.EnglishProductSubcategoryName = 'Road Bikes' )
OPTION ( LABEL = N'CustomJoin', HASH JOIN ) ;

DELETE tableA WHERE EXISTS (
SELECT TOP 1 1 FROM tableB tb WHERE tb.col1 = tableA.col1
)

DELETE dbo.Table2
FROM dbo.Table2
    INNER JOIN dbo.Table1
    ON (dbo.Table2.ColA = dbo.Table1.ColA)
    WHERE dboTable2.ColA = 1;
