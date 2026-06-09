--------------------------------------
-- TPC-DS 96
--------------------------------------
SELECT Count(*) AS "_col_0"
FROM   store_sales,
       household_demographics,
       time_dim,
       store
WHERE  ss_sold_time_sk = time_dim.t_time_sk
       AND ss_hdemo_sk = household_demographics.hd_demo_sk
       AND ss_store_sk = s_store_sk
       AND time_dim.t_hour = 15
       AND time_dim.t_minute >= 30
       AND household_demographics.hd_dep_count = 7
       AND store.s_store_name = 'ese'
ORDER  BY Count(*)
LIMIT 100;
SELECT
  COUNT(*) AS "_col_0"
FROM "store_sales" AS "store_sales"
JOIN "household_demographics" AS "household_demographics"
  ON "household_demographics"."hd_demo_sk" = "store_sales"."ss_hdemo_sk"
  AND "household_demographics"."hd_dep_count" = 7
JOIN "store" AS "store"
  ON "store"."s_store_name" = 'ese'
  AND "store"."s_store_sk" = "store_sales"."ss_store_sk"
JOIN "time_dim" AS "time_dim"
  ON "store_sales"."ss_sold_time_sk" = "time_dim"."t_time_sk"
  AND "time_dim"."t_hour" = 15
  AND "time_dim"."t_minute" >= 30
ORDER BY
  COUNT(*)
LIMIT 100;
