/*
https://learn.microsoft.com/en-us/sql/t-sql/functions/openjson-transact-sql?view=sql-server-ver16#examples
*/

SELECT *
FROM products
INNER JOIN OPENJSON(N'[1,2,3,4]') AS productTypes
  ON product.productTypeID = productTypes.value
;

SELECT * FROM OPENJSON(@json)
        WITH (  month VARCHAR(3),
                temp int,
                month_id tinyint '$.sql:identity()') as months
;

SELECT *
FROM OPENJSON ( @json )
WITH (
              Number   VARCHAR(200)   '$.Order.Number',
              Date     DATETIME       '$.Order.Date',
              Customer VARCHAR(200)   '$.AccountNumber',
              Quantity INT            '$.Item.Quantity',
              [Order]  NVARCHAR(MAX)  AS JSON
);

SELECT SalesOrderID, OrderDate, value AS Reason
FROM Sales.SalesOrderHeader
     CROSS APPLY OPENJSON (SalesReasons) WITH (value NVARCHAR(100) '$')
;

SELECT store.title, location.street, location.lat, location.long
FROM store
CROSS APPLY OPENJSON(store.jsonCol, 'lax $.location')
     WITH (street VARCHAR(500) ,  postcode VARCHAR(500) '$.postcode' ,
     lon int '$.geo.longitude', lat int '$.geo.latitude')
     AS location
;

INSERT INTO Person
SELECT *
FROM OPENJSON(@json)
WITH (id INT,
      firstName NVARCHAR(50), lastName NVARCHAR(50),
      isAlive BIT, age INT,
      dateOfBirth DATETIME, spouse NVARCHAR(50))
;

SELECT root.[key] AS [Order],TheValues.[key], TheValues.[value]
FROM OPENJSON ( @JSON ) AS root
CROSS APPLY OPENJSON ( root.value) AS TheValues
;
