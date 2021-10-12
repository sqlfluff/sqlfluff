-- Test BigQuery specific date identifiers.
SELECT
  gmv._merchant_key,
  gmv.order_created_at,
  EXTRACT(DATE FROM gmv.order_created_at) AS order_dt
FROM  my_table as gmv
WHERE gmv.datetime >= DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR), year)
LIMIT 1
