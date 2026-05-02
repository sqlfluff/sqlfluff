/* T-SQL CONTAINSTABLE examples. */

SELECT *
FROM CONTAINSTABLE(Flags, FlagColors, 'Green') AS KEY_TBL
ORDER BY KEY_TBL.RANK DESC;

SELECT FT_TBL.Name,
       KEY_TBL.RANK
FROM Production.Product AS FT_TBL
     INNER JOIN CONTAINSTABLE(
         Production.Product,
         (Name, ProductNumber),
         'ISABOUT (frame WEIGHT (.8), wheel WEIGHT (.4), tire WEIGHT (.2))',
         LANGUAGE N'English',
         5
     ) AS KEY_TBL
         ON FT_TBL.ProductID = KEY_TBL.[KEY]
ORDER BY KEY_TBL.RANK DESC;

SELECT FT_TBL.ProductDescriptionID,
       FT_TBL.Description,
       KEY_TBL.RANK
FROM Production.ProductDescription AS FT_TBL
     INNER JOIN CONTAINSTABLE(
         Production.ProductDescription,
         *,
         '(light NEAR aluminum) OR (lightweight NEAR aluminum)',
         5
     ) AS KEY_TBL
         ON FT_TBL.ProductDescriptionID = KEY_TBL.[KEY];
