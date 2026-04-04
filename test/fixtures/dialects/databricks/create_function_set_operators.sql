-- Create a table-valued function with a set operator in the RETURN body
CREATE FUNCTION example_function()
RETURNS TABLE
RETURN
SELECT 1 AS col
UNION ALL
SELECT 2 AS col
;
