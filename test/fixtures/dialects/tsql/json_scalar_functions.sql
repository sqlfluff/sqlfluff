-- Test ISJSON function
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/isjson-transact-sql

-- Basic ISJSON
SELECT ISJSON('{"name":"John"}');

-- ISJSON with column
SELECT ISJSON(json_column) FROM table1;

-- ISJSON with parameter
SELECT ISJSON(@json_data);

-- ISJSON with json_type_constraint (SQL Server 2022+)
SELECT ISJSON('{"name":"John"}', VALUE);
SELECT ISJSON('[1,2,3]', ARRAY);
SELECT ISJSON('{"key":"value"}', OBJECT);
SELECT ISJSON('"scalar"', SCALAR);

-- ISJSON in WHERE clause
SELECT * FROM table1 WHERE ISJSON(json_column) = 1;

-- ISJSON in CASE expression
SELECT CASE WHEN ISJSON(data) = 1 THEN 'Valid' ELSE 'Invalid' END FROM table1;

-- Test JSON_VALUE function
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/json-value-transact-sql

-- Basic JSON_VALUE
SELECT JSON_VALUE('{"name":"John"}', '$.name');

-- JSON_VALUE with column
SELECT JSON_VALUE(json_column, '$.address.city') FROM customers;

-- JSON_VALUE with parameter
SELECT JSON_VALUE(@json_data, '$.id');

-- JSON_VALUE with RETURNING clause
SELECT JSON_VALUE('{"age":30}', '$.age' RETURNING int);
SELECT JSON_VALUE('{"price":99.99}', '$.price' RETURNING decimal(10,2));
SELECT JSON_VALUE('{"created":"2024-01-01"}', '$.created' RETURNING datetime2);

-- JSON_VALUE with complex path
SELECT JSON_VALUE('{"users":[{"name":"John"},{"name":"Jane"}]}', '$.users[0].name');

-- JSON_VALUE in SELECT list
SELECT id, JSON_VALUE(data, '$.name') AS name, JSON_VALUE(data, '$.email') AS email FROM users;

-- Test JSON_QUERY function
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/json-query-transact-sql

-- Basic JSON_QUERY
SELECT JSON_QUERY('{"items":[1,2,3]}', '$.items');

-- JSON_QUERY with column
SELECT JSON_QUERY(json_column, '$.address') FROM customers;

-- JSON_QUERY without path (returns entire JSON)
SELECT JSON_QUERY('{"name":"John"}');

-- JSON_QUERY with parameter
SELECT JSON_QUERY(@json_data, '$.orders');

-- JSON_QUERY with WITH ARRAY WRAPPER (SQL Server 2025+)
SELECT JSON_QUERY('{"name":"John"}', '$.name' WITH ARRAY WRAPPER);

-- JSON_QUERY with complex path
SELECT JSON_QUERY('{"data":{"items":[1,2,3]}}', '$.data.items');

-- Test JSON_MODIFY function
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/json-modify-transact-sql

-- Basic JSON_MODIFY
SELECT JSON_MODIFY('{"name":"John"}', '$.name', 'Jane');

-- JSON_MODIFY with column
UPDATE customers SET json_data = JSON_MODIFY(json_data, '$.email', 'new@email.com');

-- JSON_MODIFY with parameter
SELECT JSON_MODIFY(@json_data, '$.status', 'active');

-- JSON_MODIFY adding new property
SELECT JSON_MODIFY('{"name":"John"}', '$.age', 30);

-- JSON_MODIFY with NULL to delete property
SELECT JSON_MODIFY('{"name":"John","age":30}', '$.age', NULL);

-- JSON_MODIFY with append mode
SELECT JSON_MODIFY('{"items":[1,2]}', 'append $.items', 3);

-- JSON_MODIFY nested updates
SELECT JSON_MODIFY('{"user":{"name":"John"}}', '$.user.email', 'john@example.com');

-- JSON_MODIFY with array index
SELECT JSON_MODIFY('{"items":[1,2,3]}', '$.items[1]', 99);

-- Test JSON_PATH_EXISTS function
-- https://learn.microsoft.com/en-us/sql/t-sql/functions/json-path-exists-transact-sql

-- Basic JSON_PATH_EXISTS
SELECT JSON_PATH_EXISTS('{"name":"John"}', '$.name');

-- JSON_PATH_EXISTS with column
SELECT JSON_PATH_EXISTS(json_column, '$.address.city') FROM customers;

-- JSON_PATH_EXISTS with parameter
SELECT JSON_PATH_EXISTS(@json_data, '$.user.id');

-- JSON_PATH_EXISTS in WHERE clause
SELECT * FROM table1 WHERE JSON_PATH_EXISTS(data, '$.email') = 1;

-- JSON_PATH_EXISTS with complex path
SELECT JSON_PATH_EXISTS('{"users":[{"id":1},{"id":2}]}', '$.users[0].id');

-- JSON_PATH_EXISTS checking array element
SELECT JSON_PATH_EXISTS('{"items":[1,2,3]}', '$.items[5]');

-- Combined usage examples

-- Multiple JSON functions in one query
SELECT
    id,
    ISJSON(data) AS is_valid,
    JSON_VALUE(data, '$.name') AS name,
    JSON_QUERY(data, '$.address') AS address,
    JSON_PATH_EXISTS(data, '$.email') AS has_email
FROM customers;

-- Nested JSON functions
SELECT JSON_VALUE(
    JSON_MODIFY('{"name":"John"}', '$.age', 30),
    '$.age'
);

-- JSON functions with JOIN
SELECT
    t1.id,
    JSON_VALUE(t1.data, '$.name') AS name,
    JSON_VALUE(t2.details, '$.status') AS status
FROM table1 t1
JOIN table2 t2 ON t1.id = t2.parent_id
WHERE ISJSON(t1.data) = 1;

-- JSON_VALUE with subquery
SELECT JSON_VALUE(
    (SELECT data FROM users WHERE id = 1),
    '$.email'
);

-- JSON functions with variables
DECLARE @json_string nvarchar(max) = N'{"name":"John","age":30}';
DECLARE @path nvarchar(100) = N'$.name';
SELECT JSON_VALUE(@json_string, @path);

-- JSON functions with CTE
WITH json_data AS (
    SELECT '{"items":[{"id":1,"name":"A"},{"id":2,"name":"B"}]}' AS data
)
SELECT
    JSON_VALUE(data, '$.items[0].name') AS first_item,
    JSON_VALUE(data, '$.items[1].name') AS second_item
FROM json_data;
