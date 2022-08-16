SELECT
  ID
, COALESCE(a, 1) AS CoalesceOutput
, DataDate
FROM temp1
