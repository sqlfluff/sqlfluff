SELECT * FROM employee SEMI JOIN department ON employee.deptno = department.deptno;
SELECT * FROM employee ANTI JOIN department ON employee.deptno = department.deptno;
SELECT * FROM employee LEFT SEMI JOIN department ON employee.deptno = department.deptno;
SELECT * FROM employee LEFT ANTI JOIN department ON employee.deptno = department.deptno;
