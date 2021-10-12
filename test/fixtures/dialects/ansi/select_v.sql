-- Test Nested WITH
WITH counter AS (
  WITH ladder AS (
    SELECT 1
  )
  SELECT *
  FROM ladder
  ORDER BY 1
)
SELECT *
FROM counter
