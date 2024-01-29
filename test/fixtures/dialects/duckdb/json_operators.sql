-- https://duckdb.org/docs/extensions/json#json-extraction-functions

-- Get JSON array element (indexed from zero, negative integers count from the end)
SELECT '[{"a":"foo"},{"b":"bar"},{"c":"baz"}]'::json->2;
-- Get JSON object field by key
SELECT '{"a": {"b":"foo"}}'::json->'a';
-- Get JSON array element as text
SELECT '[1,2,3]'::json->>2;
-- Get JSON object field as text
SELECT '{"a":1,"b":2}'::json->>'b';
