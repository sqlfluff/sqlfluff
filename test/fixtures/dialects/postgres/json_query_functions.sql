-- SQL/JSON query functions (PostgreSQL 17)
-- https://www.postgresql.org/docs/17/functions-json.html#FUNCTIONS-SQLJSON-QUERYING

SELECT JSON_EXISTS(jsonb '{"key1": [1,2,3]}', 'strict $.key1[*] ? (@ > $x)' PASSING 2 AS x);

SELECT JSON_EXISTS(jsonb '{"a": [1,2,3]}', 'lax $.a[5]' ERROR ON ERROR);

SELECT json_exists(js, '$.a' TRUE ON ERROR) FROM t;

SELECT JSON_QUERY(jsonb '[1,[2,3],null]', 'lax $[*][$off]' PASSING 1 AS off WITH CONDITIONAL WRAPPER);

SELECT JSON_QUERY(jsonb '{"a": "[1, 2]"}', '$.a' OMIT QUOTES);

SELECT JSON_QUERY(jsonb '{"a": "[1, 2]"}', '$.a' RETURNING int[] OMIT QUOTES ERROR ON ERROR);

SELECT JSON_QUERY(js, '$.a' WITH UNCONDITIONAL ARRAY WRAPPER KEEP QUOTES ON SCALAR STRING) FROM t;

SELECT JSON_QUERY(js, '$.a' WITHOUT ARRAY WRAPPER) FROM t;

SELECT JSON_QUERY(js, '$.a' RETURNING jsonb EMPTY ARRAY ON EMPTY EMPTY OBJECT ON ERROR) FROM t;

SELECT JSON_QUERY(js FORMAT JSON, '$.a' RETURNING text FORMAT JSON ENCODING UTF8) FROM t;

SELECT JSON_VALUE(jsonb '"123.45"', '$' RETURNING float);

SELECT JSON_VALUE(jsonb '[1,2]', 'strict $[$off]' PASSING 1 AS off);

SELECT JSON_VALUE(jsonb '[1,2]', 'strict $[*]' DEFAULT 9 ON ERROR);

SELECT JSON_VALUE(js, '$.a' RETURNING int DEFAULT 0 ON EMPTY NULL ON ERROR) FROM t;

SELECT
    JSON_VALUE(js, '$.ts' RETURNING timestamp with time zone ERROR ON ERROR) AS ts
FROM t
WHERE JSON_EXISTS(js, '$.ts');
