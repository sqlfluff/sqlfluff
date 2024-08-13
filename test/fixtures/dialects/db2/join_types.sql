-- inner join
SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
INNER JOIN department
    ON employee.deptno = department.deptno;

-- left join
SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
LEFT JOIN department
    ON employee.deptno = department.deptno;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
LEFT OUTER JOIN department
    ON employee.deptno = department.deptno;

-- right join
SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
RIGHT JOIN department
    ON employee.deptno = department.deptno;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
RIGHT OUTER JOIN department
    ON employee.deptno = department.deptno;

-- full join
SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
FULL JOIN department
    ON employee.deptno = department.deptno;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
FULL OUTER JOIN department
    ON employee.deptno = department.deptno;

-- cross join
SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee CROSS JOIN department;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee, department;
