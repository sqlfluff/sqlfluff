-- Drop FUNCTION with all optional syntax
DROP TEMPORARY FUNCTION IF EXISTS function_name;

-- Try to drop Permanent function which is not present
DROP FUNCTION test_avg;

-- Drop Temporary function
DROP TEMPORARY FUNCTION IF EXISTS test_avg;
