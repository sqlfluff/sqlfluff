--------------------------------------
-- TPC-DS 27
--------------------------------------
SELECT i_item_id,
               s_state,
               Grouping(s_state)   g_state,
               Avg(ss_quantity)    agg1,
               Avg(ss_list_price)  agg2,
               Avg(ss_coupon_amt)  agg3,
               Avg(ss_sales_price) agg4
FROM   store_sales,
       customer_demographics,
       date_dim,
       store,
       item
WHERE  ss_sold_date_sk = d_date_sk
       AND ss_item_sk = i_item_sk
       AND ss_store_sk = s_store_sk
       AND ss_cdemo_sk = cd_demo_sk
       AND cd_gender = 'M'
       AND cd_marital_status = 'D'
       AND cd_education_status = 'College'
       AND d_year = 2000
       AND s_state IN ( 'TN', 'TN', 'TN', 'TN',
                        'TN', 'TN' )
GROUP  BY rollup ( i_item_id, s_state )
ORDER  BY i_item_id,
          s_state
LIMIT 100;
SELECT
  "item"."i_item_id" AS "i_item_id",
  "store"."s_state" AS "s_state",
  GROUPING("store"."s_state") AS "g_state",
  AVG("store_sales"."ss_quantity") AS "agg1",
  AVG("store_sales"."ss_list_price") AS "agg2",
  AVG("store_sales"."ss_coupon_amt") AS "agg3",
  AVG("store_sales"."ss_sales_price") AS "agg4"
FROM "store_sales" AS "store_sales"
JOIN "customer_demographics" AS "customer_demographics"
  ON "customer_demographics"."cd_demo_sk" = "store_sales"."ss_cdemo_sk"
  AND "customer_demographics"."cd_education_status" = 'College'
  AND "customer_demographics"."cd_gender" = 'M'
  AND "customer_demographics"."cd_marital_status" = 'D'
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  AND "date_dim"."d_year" = 2000
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
JOIN "store" AS "store"
  ON "store"."s_state" IN ('TN', 'TN', 'TN', 'TN', 'TN', 'TN')
  AND "store"."s_store_sk" = "store_sales"."ss_store_sk"
GROUP BY
  ROLLUP (
    "item"."i_item_id",
    "store"."s_state"
  )
ORDER BY
  "i_item_id",
  "s_state"
LIMIT 100;
