-- Basic QUALIFY clause - SELECT must have only plain columns
SELECT
    item,
    category,
    purchases
FROM produce
QUALIFY RANK() OVER (PARTITION BY category ORDER BY purchases DESC) <= 3;

-- QUALIFY with WHERE clause
SELECT
    item,
    category,
    purchases
FROM produce
WHERE category = 'vegetable'
QUALIFY RANK() OVER (PARTITION BY category ORDER BY purchases DESC) <= 3;

-- QUALIFY with ORDER BY
SELECT
    item,
    category,
    purchases
FROM produce
WHERE category = 'vegetable'
QUALIFY RANK() OVER (PARTITION BY category ORDER BY purchases DESC) <= 3
ORDER BY item;

-- QUALIFY with LIMIT
SELECT
    item,
    category,
    purchases
FROM produce
WHERE category = 'vegetable'
QUALIFY RANK() OVER (PARTITION BY category ORDER BY purchases DESC) <= 3
LIMIT 5;

-- QUALIFY with ROW_NUMBER function
SELECT
    schema_name,
    function_name
FROM functions
QUALIFY ROW_NUMBER() OVER (PARTITION BY schema_name ORDER BY function_name) < 3;

-- QUALIFY with DENSE_RANK
SELECT
    product_id,
    sales_date,
    sales_amount
FROM sales
QUALIFY DENSE_RANK() OVER (PARTITION BY product_id ORDER BY sales_amount DESC) <= 5;

-- QUALIFY with equals comparison
SELECT
    user_id,
    event_date
FROM user_events
QUALIFY ROW_NUMBER() OVER (ORDER BY event_date) = 1;

-- QUALIFY with greater than
SELECT
    customer_id,
    order_amount
FROM orders
QUALIFY RANK() OVER (ORDER BY order_amount DESC) > 10;

-- QUALIFY with multiple columns
SELECT
    col1,
    col2,
    col3,
    col4
FROM my_table
QUALIFY ROW_NUMBER() OVER (PARTITION BY col1 ORDER BY col2 DESC) <= 100;

-- GROUP BY with QUALIFY
SELECT
    region,
    product_id
FROM sales
GROUP BY region, product_id
QUALIFY ROW_NUMBER() OVER (PARTITION BY region ORDER BY product_id) <= 5;

-- GROUP BY with HAVING and QUALIFY - SELECT only columns
SELECT
    category,
    item
FROM produce
GROUP BY category, item
HAVING COUNT(*) > 5
QUALIFY RANK() OVER (PARTITION BY category ORDER BY item) <= 3;

-- GROUP BY with HAVING, QUALIFY and WHERE
SELECT
    customer_id,
    product_id
FROM orders
WHERE order_date > '2024-01-01'
GROUP BY customer_id, product_id
HAVING SUM(order_amount) > 1000
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY product_id) = 1;

-- GROUP BY with HAVING, QUALIFY and ORDER BY
SELECT
    region,
    store_id
FROM sales
GROUP BY region, store_id
HAVING AVG(sales_amount) > 500
QUALIFY DENSE_RANK() OVER (PARTITION BY region ORDER BY store_id DESC) <= 5
ORDER BY region, store_id;

-- GROUP BY with HAVING, QUALIFY and LIMIT
SELECT
    category,
    subcategory
FROM products
GROUP BY category, subcategory
HAVING MAX(price) > 100
QUALIFY ROW_NUMBER() OVER (ORDER BY category, subcategory) <= 10
LIMIT 10;

-- GROUP BY with multiple HAVING conditions and QUALIFY
SELECT
    department,
    employee_id
FROM employees
GROUP BY department, employee_id
HAVING COUNT(*) > 1
    AND MIN(salary) > 50000
QUALIFY RANK() OVER (PARTITION BY department ORDER BY employee_id) < 100;
