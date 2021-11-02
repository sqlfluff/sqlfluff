SELECT
  ID,
DataDate,
COALESCE(a, 1) AS CoalesceOutput
FROM temp1
