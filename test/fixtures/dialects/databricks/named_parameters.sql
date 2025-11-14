-- Databricks named parameters with colon syntax
-- https://docs.databricks.com/sql/language-manual/sql-ref-parameters.html

-- Simple parameter in WHERE clause
SELECT * FROM table1 WHERE id = :param_id;

-- Multiple parameters
SELECT * FROM users WHERE name = :user_name AND age > :min_age;

-- Parameter in SELECT list
SELECT :column_name FROM table1;

-- Parameter in function call
SELECT CONCAT('Hello ', :name) FROM table1;

-- Parameter in JOIN condition
SELECT a.*, b.* FROM table1 a
JOIN table2 b ON a.id = b.id AND b.status = :status;

-- Parameter in GROUP BY/HAVING
SELECT category, COUNT(*) as cnt
FROM products
WHERE price > :min_price
GROUP BY category
HAVING COUNT(*) > :min_count;

-- Parameter in ORDER BY
SELECT * FROM table1 ORDER BY :sort_column;

-- Parameter in LIMIT
SELECT * FROM table1 LIMIT :max_rows;

-- Parameter with underscore in name
SELECT * FROM table1 WHERE id = :param_id_123;

-- Parameter in INSERT statement
INSERT INTO table1 (name, age) VALUES (:name, :age);

-- Parameter in UPDATE statement
UPDATE table1 SET status = :new_status WHERE id = :target_id;

-- Parameter in DELETE statement
DELETE FROM table1 WHERE id = :delete_id;

-- Parameter in USE CATALOG
USE CATALOG :catalog_name;

-- Parameter with IDENTIFIER clause in USE SCHEMA
USE SCHEMA IDENTIFIER(:schema_name);

-- Original error case: CREATE WIDGET with named parameter and IDENTIFIER
CREATE WIDGET DROPDOWN target_catalog DEFAULT "catalog_a" CHOICES
SELECT *
FROM (
    VALUES (
        "catalog_a"
    )
);

SHOW SCHEMAS
FROM IDENTIFIER (:target_catalog);

-- Test colon accessor vs parameter: ensure data:field is not parsed as :field parameter
SELECT
    json_data:name,
    json_data:address:city,
    :param_value
FROM table1
WHERE json_data:id > :min_id;
