-- FOR JSON

SELECT name, surname
FROM emp
FOR JSON AUTO;
GO

SELECT 1 AS a
FOR JSON PATH;
GO

SELECT 1 AS a
FOR JSON PATH, WITHOUT_ARRAY_WRAPPER
GO

SELECT c.ClassName,
    s.StudentName
FROM #tabClass AS c
RIGHT JOIN #tabStudent AS s ON s.ClassGuid = c.ClassGuid
ORDER BY c.ClassName,
    s.StudentName
FOR JSON AUTO;
GO

SELECT 1 AS a
FOR JSON PATH, ROOT ('RootName'), WITHOUT_ARRAY_WRAPPER, INCLUDE_NULL_VALUES;
GO

-- FOR XML

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

-- Per Issue #5567
SELECT 0 ErrorCode
FOR XML PATH('Result'), TYPE

-- FOR BROWSE
SELECT 1 AS a
FOR BROWSE
GO
