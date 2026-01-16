SELECT
  ARRAY_AGG(cors_origin_value IGNORE NULLS LIMIT 5) AS sample_cors_origins
FROM
  table1
