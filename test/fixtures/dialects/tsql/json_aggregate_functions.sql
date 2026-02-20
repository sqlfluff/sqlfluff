-- Test JSON_ARRAYAGG function
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/json-functions-transact-sql

-- Basic JSON_ARRAYAGG
SELECT JSON_ARRAYAGG(name) FROM employees;

-- JSON_ARRAYAGG with column expression
SELECT JSON_ARRAYAGG(employee_id) FROM departments;

-- JSON_ARRAYAGG with NULL ON NULL
SELECT JSON_ARRAYAGG(department_name NULL ON NULL) FROM departments;

-- JSON_ARRAYAGG with ABSENT ON NULL
SELECT JSON_ARRAYAGG(manager_name ABSENT ON NULL) FROM departments;

-- JSON_ARRAYAGG with RETURNING clause
SELECT JSON_ARRAYAGG(product_id RETURNING json) FROM products;

-- JSON_ARRAYAGG with complex expression
SELECT JSON_ARRAYAGG(first_name + ' ' + last_name) FROM employees;

-- JSON_ARRAYAGG with WITHIN GROUP (ORDER BY)
SELECT JSON_ARRAYAGG(name) WITHIN GROUP (ORDER BY hire_date) FROM employees;

-- JSON_ARRAYAGG with WITHIN GROUP and NULL handling
SELECT JSON_ARRAYAGG(salary NULL ON NULL) WITHIN GROUP (ORDER BY salary DESC) FROM employees;

-- JSON_ARRAYAGG with WITHIN GROUP and OVER (PARTITION BY)
SELECT
    department_id,
    JSON_ARRAYAGG(employee_name) WITHIN GROUP (ORDER BY employee_id) OVER (PARTITION BY department_id)
FROM employees;

-- JSON_ARRAYAGG with GROUP BY
SELECT
    department_id,
    JSON_ARRAYAGG(employee_name) AS employee_names
FROM employees
GROUP BY department_id;

-- JSON_ARRAYAGG with multiple ORDER BY columns in WITHIN GROUP
SELECT JSON_ARRAYAGG(name) WITHIN GROUP (ORDER BY last_name, first_name) FROM employees;

-- Test JSON_OBJECTAGG function
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/json-functions-transact-sql

-- Basic JSON_OBJECTAGG
SELECT JSON_OBJECTAGG(name:value) FROM settings;

-- JSON_OBJECTAGG with column references
SELECT JSON_OBJECTAGG(key_column:value_column) FROM config;

-- JSON_OBJECTAGG with NULL ON NULL
SELECT JSON_OBJECTAGG(setting_name:setting_value NULL ON NULL) FROM settings;

-- JSON_OBJECTAGG with ABSENT ON NULL
SELECT JSON_OBJECTAGG(config_key:config_value ABSENT ON NULL) FROM configuration;

-- JSON_OBJECTAGG with RETURNING clause
SELECT JSON_OBJECTAGG(prop_name:prop_value RETURNING json) FROM properties;

-- JSON_OBJECTAGG with WITHIN GROUP (ORDER BY)
SELECT JSON_OBJECTAGG(name:score) WITHIN GROUP (ORDER BY score DESC) FROM leaderboard;

-- JSON_OBJECTAGG with WITHIN GROUP and NULL handling
SELECT JSON_OBJECTAGG(attr_name:attr_value ABSENT ON NULL) WITHIN GROUP (ORDER BY attr_name) FROM attributes;

-- JSON_OBJECTAGG with WITHIN GROUP and OVER (PARTITION BY)
SELECT
    category,
    JSON_OBJECTAGG(item_name:item_price) WITHIN GROUP (ORDER BY item_name) OVER (PARTITION BY category)
FROM products;

-- JSON_OBJECTAGG with GROUP BY
SELECT
    user_id,
    JSON_OBJECTAGG(setting_name:setting_value) AS user_settings
FROM user_preferences
GROUP BY user_id;

-- JSON_OBJECTAGG with literal key
SELECT JSON_OBJECTAGG('key':value_column) FROM table1;

-- JSON_OBJECTAGG with concatenated key
SELECT JSON_OBJECTAGG(prefix + '_' + suffix:data_value) FROM data_table;

-- Combined usage examples

-- Nested aggregation with JSON_ARRAYAGG and JSON_OBJECTAGG
SELECT
    department_id,
    JSON_OBJECTAGG(
        employee_id:employee_name
    ) AS employees
FROM employees
GROUP BY department_id;

-- Multiple JSON aggregate functions in one query
SELECT
    department_id,
    JSON_ARRAYAGG(employee_name) AS names,
    JSON_OBJECTAGG(employee_id:employee_email) AS contacts
FROM employees
GROUP BY department_id;

-- JSON aggregate functions with CASE expressions
SELECT JSON_ARRAYAGG(
    CASE
        WHEN salary > 50000 THEN 'High'
        ELSE 'Low'
    END
) FROM employees;

-- JSON_OBJECTAGG with computed values
SELECT JSON_OBJECTAGG(
    product_name:(quantity * price)
) FROM order_items;

-- JSON aggregate functions in CTE
WITH employee_data AS (
    SELECT
        department_id,
        employee_name,
        salary
    FROM employees
)
SELECT
    department_id,
    JSON_ARRAYAGG(employee_name) WITHIN GROUP (ORDER BY salary DESC) AS employees_by_salary
FROM employee_data
GROUP BY department_id;

-- JSON aggregate functions with JOIN
SELECT
    d.department_name,
    JSON_ARRAYAGG(e.employee_name) AS employees
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_name;

-- Complex nesting with both JSON constructor and aggregate functions
SELECT
    category,
    JSON_OBJECT(
        'items': JSON_ARRAYAGG(product_name),
        'count': COUNT(*)
    )
FROM products
GROUP BY category;

-- JSON_ARRAYAGG with NULL values and different NULL handling
SELECT
    'with_nulls' AS type,
    JSON_ARRAYAGG(nullable_column NULL ON NULL) AS result
FROM test_data
UNION ALL
SELECT
    'without_nulls' AS type,
    JSON_ARRAYAGG(nullable_column ABSENT ON NULL) AS result
FROM test_data;

-- JSON_OBJECTAGG with subquery values
SELECT JSON_OBJECTAGG(
    user_id:(SELECT COUNT(*) FROM orders WHERE orders.user_id = users.id)
) FROM users;
