CREATE VIEW vwCTE AS
--Creates an infinite loop
WITH cte (EmployeeID, ManagerID, Title) AS
(
    SELECT EmployeeID, ManagerID, Title
    FROM HumanResources.Employee
    WHERE ManagerID IS NOT NULL
  UNION ALL
    SELECT cte.EmployeeID, cte.ManagerID, cte.Title
    FROM cte
    JOIN  HumanResources.Employee AS e
        ON cte.ManagerID = e.EmployeeID
)
-- Notice the MAXRECURSION option is removed
SELECT EmployeeID, ManagerID, Title
FROM cte
GO
