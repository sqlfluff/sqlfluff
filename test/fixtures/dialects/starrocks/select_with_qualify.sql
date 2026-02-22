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
