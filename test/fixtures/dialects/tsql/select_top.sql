select top 1 t.date_column1 as last_date_column1
from
	t1.t2.table_name t
order by
	t.column1 desc;

SELECT TOP(10)JobTitle, HireDate
FROM HumanResources.Employee;

SELECT TOP(10)JobTitle, HireDate
FROM HumanResources.Employee
ORDER BY HireDate DESC;

SELECT TOP(5)PERCENT JobTitle, HireDate
FROM HumanResources.Employee
ORDER BY HireDate DESC;

SELECT TOP(10) PERCENT WITH TIES
pp.FirstName, pp.LastName, e.JobTitle, e.Gender, r.Rate
FROM Person.Person AS pp
    INNER JOIN HumanResources.Employee AS e
        ON pp.BusinessEntityID = e.BusinessEntityID
    INNER JOIN HumanResources.EmployeePayHistory AS r
        ON r.BusinessEntityID = e.BusinessEntityID
ORDER BY Rate DESC;
