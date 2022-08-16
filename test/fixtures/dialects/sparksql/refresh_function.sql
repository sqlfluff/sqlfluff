-- The cached entry of the function will be refreshed
-- The function is resolved from the current database
--   as the function name is unqualified.
REFRESH FUNCTION func1;

-- The cached entry of the function will be refreshed
-- The function is resolved from tempDB database as the
--   function name is qualified.
REFRESH FUNCTION db1.func1;
