SELECT ProductModelID, Name
FROM Production.ProductModel
WHERE ProductModelID=122 or ProductModelID=119
FOR XML RAW;

SELECT ProductPhotoID, ThumbNailPhoto
FROM   Production.ProductPhoto
WHERE ProductPhotoID=70
FOR XML AUTO;

SELECT 1    as Tag
FROM   HumanResources.Employee AS E
FOR XML EXPLICIT;

SELECT
    ProductModelID,
    Name
FROM Production.ProductModel
WHERE ProductModelID=122 OR ProductModelID=119
FOR XML PATH ('root');
