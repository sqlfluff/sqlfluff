-- inner join
SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
INNER JOIN department
    ON employee.deptno = department.deptno;

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
NATURAL INNER JOIN department
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

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
NATURAL LEFT OUTER JOIN department
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

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
NATURAL RIGHT OUTER JOIN department
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

SELECT
    employee.id,
    employee.name,
    employee.deptno,
    department.deptname
FROM employee
NATURAL FULL OUTER JOIN department
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

-- semi join

SELECT /*+ syntactic_join */ product_dimension.product_description AS product_description
FROM (public.product_dimension AS product_dimension/*+projs('public.product_dimension')*/
SEMI JOIN /*+Distrib(F,R),JType(H)*/ (SELECT inventory_fact.qty_in_stock AS qty_in_stock
FROM public.inventory_fact AS inventory_fact/*+projs('public.inventory_fact')*/) AS subQ_1
ON (product_dimension.product_key = subQ_1.qty_in_stock));

-- nullaware anti join

SELECT /*+ syntactic_join */ product_dimension.product_description AS product_description
FROM (public.product_dimension AS product_dimension/*+projs('public.product_dimension')*/
NULLAWARE ANTI JOIN /*+Distrib(L,B),JType(H)*/ (SELECT inventory_fact.qty_in_stock AS qty_in_stock
FROM public.inventory_fact AS inventory_fact/*+projs('public.inventory_fact')*/) AS subQ_1
ON (product_dimension.product_key = subQ_1.qty_in_stock));

-- semiall join

SELECT /*+ syntactic_join */ product_dimension.product_key AS product_key, product_dimension.product_description AS product_description
FROM (public.product_dimension AS product_dimension/*+projs('public.product_dimension')*/
SEMIALL JOIN /*+Distrib(F,B),JType(H)*/ (SELECT inventory_fact.product_key AS product_key FROM public.inventory_fact AS inventory_fact/*+projs('public.inventory_fact')*/) AS subQ_1
ON (product_dimension.product_key > subQ_1.product_key));

-- anti join

SELECT /*+ syntactic_join */ product_dimension.product_key AS product_key, product_dimension.product_description AS product_description
FROM (public.product_dimension AS product_dimension/*+projs('public.product_dimension')*/
ANTI JOIN /*+Distrib(F,L),JType(H)*/ (SELECT inventory_fact.product_key AS "inventory_fact.product_key"
FROM public.inventory_fact AS inventory_fact/*+projs('public.inventory_fact')*/) AS subQ_1
ON (subQ_1."inventory_fact.product_key" = product_dimension.product_key));
