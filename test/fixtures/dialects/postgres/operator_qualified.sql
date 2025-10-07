-- Test OPERATOR() syntax for qualified operator references
-- https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-OPERATORS
-- Note: Currently only single-character operators are supported

-- Basic comparison operators with schema qualification
SELECT *
FROM table1
WHERE col1 OPERATOR (public.=) 'value1';

SELECT *
FROM table1
WHERE col3 OPERATOR (myschema.>) 100;

SELECT *
FROM table1
WHERE col4 OPERATOR (myschema.<) 100;

-- Arithmetic operators
SELECT col1 OPERATOR (public.+) col2 AS sum_result
FROM table1;

SELECT col1 OPERATOR (public.-) col2 AS diff_result
FROM table1;

SELECT col1 OPERATOR (public.*) col2 AS mult_result
FROM table1;

SELECT col1 OPERATOR (public./) col2 AS div_result
FROM table1;

-- OPERATOR in HAVING clause
SELECT category, COUNT(*)
FROM products
GROUP BY category
HAVING COUNT(*) OPERATOR (public.>) 5;

-- OPERATOR in JOIN condition
SELECT t1.id, t2.name
FROM table1 AS t1
INNER JOIN table2 AS t2 ON t1.id OPERATOR (public.=) t2.table1_id;

-- OPERATOR in CASE expression
SELECT
    CASE
        WHEN value OPERATOR (public.>) 100 THEN 'high'
        WHEN value OPERATOR (public.<) 100 THEN 'low'
    END AS category
FROM measurements;

-- Multiple schema names
SELECT *
FROM table1
WHERE col1 OPERATOR (schema1.=) val1
  AND col2 OPERATOR (schema2.>) val2;
