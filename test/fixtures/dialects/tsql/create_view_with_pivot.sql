CREATE OR ALTER VIEW DEST.V_HOSPITAL_ADMISSIONS_OVERTIME_BYAGEGROUP
AS
    -- Pivot table with one row and five columns
SELECT 'AverageCost' AS Cost_Sorted_By_Production_Days,
  [0], [1], [2], [3], [4]
FROM
(
  SELECT DaysToManufacture, StandardCost
  FROM Production.Product
) AS SourceTable
PIVOT
(
  AVG(StandardCost)
  FOR DaysToManufacture IN ([0], [1], [2], [3], [4])
) AS PivotTable;
