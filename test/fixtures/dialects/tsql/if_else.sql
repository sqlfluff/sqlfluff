IF 1 <= (SELECT Weight from DimProduct WHERE ProductKey = 1)
    SELECT ProductKey, EnglishDescription, Weight, 'This product is too heavy to ship and is only available for pickup.'
        AS ShippingStatus
    FROM DimProduct WHERE ProductKey = 1
ELSE
    SELECT ProductKey, EnglishDescription, Weight, 'This product is available for shipping or pickup.'
        AS ShippingStatus
    FROM DimProduct WHERE ProductKey = 1


if exists (select * from #a union all select * from #b)
  set @var = 1;
