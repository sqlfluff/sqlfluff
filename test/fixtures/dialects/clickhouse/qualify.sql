-- Basic QUALIFY with ROW_NUMBER
SELECT *
FROM employees
QUALIFY ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) = 1;

-- QUALIFY with complex expression
SELECT
    id,
    name,
    salary
FROM employees
QUALIFY SUM(salary) OVER (PARTITION BY dept_id) > 100000;

-- QUALIFY with WHERE clause
SELECT *
FROM sales
WHERE region = 'US'
QUALIFY RANK() OVER (ORDER BY amount DESC) <= 10;

-- QUALIFY with GROUP BY and HAVING
SELECT
    dept_id,
    COUNT(*) as emp_count
FROM employees
GROUP BY dept_id
HAVING emp_count > 5
QUALIFY ROW_NUMBER() OVER (ORDER BY emp_count DESC) = 1;

-- QUALIFY in CTE
WITH ranked AS (
    SELECT
        *
    FROM orders
    QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1
)
SELECT * FROM ranked;
