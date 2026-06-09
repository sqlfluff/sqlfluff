--------------------------------------
-- TPC-DS 7
--------------------------------------
SELECT i_item_id,
               Avg(ss_quantity)    agg1,
               Avg(ss_list_price)  agg2,
               Avg(ss_coupon_amt)  agg3,
               Avg(ss_sales_price) agg4
FROM   store_sales,
       customer_demographics,
       date_dim,
       item,
       promotion
WHERE  ss_sold_date_sk = d_date_sk
       AND ss_item_sk = i_item_sk
       AND ss_cdemo_sk = cd_demo_sk
       AND ss_promo_sk = p_promo_sk
       AND cd_gender = 'F'
       AND cd_marital_status = 'W'
       AND cd_education_status = '2 yr Degree'
       AND ( p_channel_email = 'N'
              OR p_channel_event = 'N' )
       AND d_year = 1998
GROUP  BY i_item_id
ORDER  BY i_item_id
LIMIT 100;
SELECT
  "item"."i_item_id" AS "i_item_id",
  AVG("store_sales"."ss_quantity") AS "agg1",
  AVG("store_sales"."ss_list_price") AS "agg2",
  AVG("store_sales"."ss_coupon_amt") AS "agg3",
  AVG("store_sales"."ss_sales_price") AS "agg4"
FROM "store_sales" AS "store_sales"
JOIN "customer_demographics" AS "customer_demographics"
  ON "customer_demographics"."cd_demo_sk" = "store_sales"."ss_cdemo_sk"
  AND "customer_demographics"."cd_education_status" = '2 yr Degree'
  AND "customer_demographics"."cd_gender" = 'F'
  AND "customer_demographics"."cd_marital_status" = 'W'
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  AND "date_dim"."d_year" = 1998
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
JOIN "promotion" AS "promotion"
  ON (
    "promotion"."p_channel_email" = 'N' OR "promotion"."p_channel_event" = 'N'
  )
  AND "promotion"."p_promo_sk" = "store_sales"."ss_promo_sk"
GROUP BY
  "item"."i_item_id"
ORDER BY
  "i_item_id"
LIMIT 100;
