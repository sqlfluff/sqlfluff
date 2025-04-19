SELECT DeptID, DeptName, DeptMgrID, EmpID, EmpLastName, EmpSalary
FROM Departments d
CROSS APPLY dbo.GetReports(d.DeptMgrID) ;

SELECT d.DeptID, d.DeptName, DeptMgrID, reps.EmpID, reps.EmpLastName, reps.EmpSalary
FROM Departments AS d
CROSS APPLY dbo.GetReports(d.DeptMgrID) AS reps
WHERE d.DeptMgrID = 10;

SELECT * FROM Department D
OUTER APPLY dbo.fn_GetAllEmployeeOfADepartment(D.DepartmentID);


SELECT * FROM Department D
OUTER APPLY dbo.fn_GetAllEmployeeOfADepartment(D.DepartmentID) AS AllEmp
WHERE D.DepartmentId = 10;


select
	s.column_id
	, sp.value
from
	table1 as s
cross apply
	string_split(replace(s.some_path, '->', '{'), '{') as sp;
