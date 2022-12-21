-- SQL from issue #2033
SELECT COALESCE(doc#>>'{fields}','') AS field
FROM mytable
WHERE doc ->> 'some_field' = 'some_value';

-- Get JSON array element (indexed from zero, negative integers count from the end)
SELECT '[{"a":"foo"},{"b":"bar"},{"c":"baz"}]'::json->2;
-- Get JSON object field by key
SELECT '{"a": {"b":"foo"}}'::json->'a';
-- Get JSON array element as text
SELECT '[1,2,3]'::json->>2;
-- Get JSON object field as text
SELECT '{"a":1,"b":2}'::json->>'b';
-- Get JSON object at the specified path
SELECT '{"a": {"b":{"c": "foo"}}}'::json#>'{a,b}';
-- Get JSON object at the specified path as text
SELECT '{"a":[1,2,3],"b":[4,5,6]}'::json#>>'{a,2}';
