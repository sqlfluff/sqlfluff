--------------------------------------
-- TPC-DS 61
--------------------------------------
SELECT promotions,
               total,
               Cast(promotions AS DECIMAL(15, 4)) /
               Cast(total AS DECIMAL(15, 4)) * 100
FROM   (SELECT Sum(ss_ext_sales_price) promotions
        FROM   store_sales,
               store,
               promotion,
               date_dim,
               customer,
               customer_address,
               item
        WHERE  ss_sold_date_sk = d_date_sk
               AND ss_store_sk = s_store_sk
               AND ss_promo_sk = p_promo_sk
               AND ss_customer_sk = c_customer_sk
               AND ca_address_sk = c_current_addr_sk
               AND ss_item_sk = i_item_sk
               AND ca_gmt_offset = -7
               AND i_category = 'Books'
               AND ( p_channel_dmail = 'Y'
                      OR p_channel_email = 'Y'
                      OR p_channel_tv = 'Y' )
               AND s_gmt_offset = -7
               AND d_year = 2001
               AND d_moy = 12) promotional_sales,
       (SELECT Sum(ss_ext_sales_price) total
        FROM   store_sales,
               store,
               date_dim,
               customer,
               customer_address,
               item
        WHERE  ss_sold_date_sk = d_date_sk
               AND ss_store_sk = s_store_sk
               AND ss_customer_sk = c_customer_sk
               AND ca_address_sk = c_current_addr_sk
               AND ss_item_sk = i_item_sk
               AND ca_gmt_offset = -7
               AND i_category = 'Books'
               AND s_gmt_offset = -7
               AND d_year = 2001
               AND d_moy = 12) all_sales
ORDER  BY promotions,
          total
LIMIT 100;
WITH "customer_2" AS (
  SELECT
    "customer"."c_customer_sk" AS "c_customer_sk",
    "customer"."c_current_addr_sk" AS "c_current_addr_sk"
  FROM "customer" AS "customer"
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year",
    "date_dim"."d_moy" AS "d_moy"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_moy" = 12 AND "date_dim"."d_year" = 2001
), "item_2" AS (
  SELECT
    "item"."i_item_sk" AS "i_item_sk",
    "item"."i_category" AS "i_category"
  FROM "item" AS "item"
  WHERE
    "item"."i_category" = 'Books'
), "store_2" AS (
  SELECT
    "store"."s_store_sk" AS "s_store_sk",
    "store"."s_gmt_offset" AS "s_gmt_offset"
  FROM "store" AS "store"
  WHERE
    "store"."s_gmt_offset" = -7
), "customer_address_2" AS (
  SELECT
    "customer_address"."ca_address_sk" AS "ca_address_sk",
    "customer_address"."ca_gmt_offset" AS "ca_gmt_offset"
  FROM "customer_address" AS "customer_address"
  WHERE
    "customer_address"."ca_gmt_offset" = -7
), "promotional_sales" AS (
  SELECT
    SUM("store_sales"."ss_ext_sales_price") AS "promotions"
  FROM "store_sales" AS "store_sales"
  JOIN "customer_2" AS "customer"
    ON "customer"."c_customer_sk" = "store_sales"."ss_customer_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "promotion" AS "promotion"
    ON (
      "promotion"."p_channel_dmail" = 'Y'
      OR "promotion"."p_channel_email" = 'Y'
      OR "promotion"."p_channel_tv" = 'Y'
    )
    AND "promotion"."p_promo_sk" = "store_sales"."ss_promo_sk"
  JOIN "store_2" AS "store"
    ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
  JOIN "customer_address_2" AS "customer_address"
    ON "customer"."c_current_addr_sk" = "customer_address"."ca_address_sk"
), "all_sales" AS (
  SELECT
    SUM("store_sales"."ss_ext_sales_price") AS "total"
  FROM "store_sales" AS "store_sales"
  JOIN "customer_2" AS "customer"
    ON "customer"."c_customer_sk" = "store_sales"."ss_customer_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "store_2" AS "store"
    ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
  JOIN "customer_address_2" AS "customer_address"
    ON "customer"."c_current_addr_sk" = "customer_address"."ca_address_sk"
)
SELECT
  "promotional_sales"."promotions" AS "promotions",
  "all_sales"."total" AS "total",
  CAST("promotional_sales"."promotions" AS DECIMAL(15, 4)) / CAST("all_sales"."total" AS DECIMAL(15, 4)) * 100 AS "_col_2"
FROM "promotional_sales" AS "promotional_sales"
CROSS JOIN "all_sales" AS "all_sales"
ORDER BY
  "promotions",
  "total"
LIMIT 100;
