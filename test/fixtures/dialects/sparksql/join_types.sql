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

-- right join
SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
RIGHT JOIN department
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

-- semi join
SELECT employee.id -- noqa: L031
FROM employee
SEMI JOIN department
    ON employee.deptno = department.deptno;

SELECT employee.id
FROM employee
LEFT SEMI JOIN department
    ON employee.deptno = department.deptno;

-- anti join
SELECT employee.id
FROM employee
ANTI JOIN department
    ON employee.deptno = department.deptno;

SELECT employee.id
FROM employee
LEFT ANTI JOIN department
    ON employee.deptno = department.deptno;

-- natural joins
SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee NATURAL INNER JOIN department;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee NATURAL LEFT JOIN department;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee NATURAL RIGHT JOIN department;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee NATURAL FULL JOIN department;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee NATURAL FULL OUTER JOIN department;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee NATURAL CROSS JOIN department;

SELECT employee.id FROM employee NATURAL SEMI JOIN department;

SELECT employee.id FROM employee NATURAL LEFT SEMI JOIN department;

SELECT employee.id FROM employee NATURAL ANTI JOIN department;

SELECT employee.id FROM employee NATURAL LEFT ANTI JOIN department;

-- Multiple join
SELECT
    table1.a,
    table2.b,
    table3.c
FROM table1
INNER JOIN table2
    ON table1.a = table2.a
INNER JOIN table3
    ON table1.a = table3.a
