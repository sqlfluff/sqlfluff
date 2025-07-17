-- PostgreSQL 16 IS JSON syntax tests
-- Based on: https://www.postgresql.org/docs/16/functions-json.html#FUNCTIONS-SQLJSON-MISC

-- Basic IS JSON syntax
SELECT '{}' IS JSON;
SELECT '[]' IS JSON;
SELECT '"test"' IS JSON;
SELECT 'invalid' IS JSON;

-- IS NOT JSON syntax
SELECT 'invalid' IS NOT JSON;
SELECT '{}' IS NOT JSON;

-- IS JSON with type specification
SELECT '{}' IS JSON OBJECT;
SELECT '[]' IS JSON ARRAY;
SELECT '"test"' IS JSON SCALAR;
SELECT '{"a": 1}' IS JSON VALUE;

-- IS NOT JSON with type specification
SELECT '"test"' IS NOT JSON OBJECT;
SELECT '{}' IS NOT JSON ARRAY;
SELECT '[]' IS NOT JSON SCALAR;
SELECT 'invalid' IS NOT JSON VALUE;

-- IS JSON with UNIQUE KEYS
SELECT '{"a": 1, "b": 2}' IS JSON WITH UNIQUE KEYS;
SELECT '{"a": 1, "a": 2}' IS JSON WITH UNIQUE KEYS;
SELECT '{"a": 1, "b": 2}' IS JSON WITHOUT UNIQUE KEYS;

-- IS JSON with type and unique keys
SELECT '{"a": 1, "b": 2}' IS JSON OBJECT WITH UNIQUE KEYS;
SELECT '{"a": 1, "a": 2}' IS JSON OBJECT WITH UNIQUE KEYS;
SELECT '{"a": 1, "b": 2}' IS JSON OBJECT WITHOUT UNIQUE KEYS;

-- IS NOT JSON with type and unique keys
SELECT '[]' IS NOT JSON OBJECT WITH UNIQUE KEYS;
SELECT '[1, 2]' IS NOT JSON OBJECT WITHOUT UNIQUE KEYS;

-- Complex expressions with IS JSON
SELECT col1 IS JSON, col2 IS NOT JSON ARRAY FROM table1;
SELECT CASE WHEN data IS JSON OBJECT THEN 'valid' ELSE 'invalid' END FROM table1;

-- IS JSON in WHERE clauses
SELECT * FROM table1 WHERE data IS JSON;
SELECT * FROM table1 WHERE config IS NOT JSON OBJECT;
SELECT * FROM table1 WHERE metadata IS JSON WITH UNIQUE KEYS;

-- IS JSON with column expressions
SELECT (column_name::text) IS JSON FROM table1;
SELECT COALESCE(data, '{}') IS JSON OBJECT FROM table1;
