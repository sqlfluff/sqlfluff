SELECT DeptID, DeptName, DeptMgrID, EmpID, EmpLastName, EmpSalary  
FROM Departments d    
CROSS APPLY dbo.GetReports(d.DeptMgrID) ;  

SELECT * FROM Department D 
OUTER APPLY dbo.fn_GetAllEmployeeOfADepartment(D.DepartmentID);

select
	s.column_id
	, sp.value 
from
	table1 as s
cross apply 
	string_split(replace(s.some_path, '->', '{'), '{') as sp;
