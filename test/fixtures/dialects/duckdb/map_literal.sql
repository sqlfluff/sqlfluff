-- https://duckdb.org/docs/stable/sql/data_types/map
-- Map literal with string keys
SELECT MAP {'key1': 50, 'key2': 75};
-- Map literal with integer keys
SELECT MAP {1: 'a', 2: 'b'};
-- Empty map literal
SELECT MAP {};
-- Map with IN operator
SELECT 'key1' IN MAP {'key1': 50, 'key2': 75};
