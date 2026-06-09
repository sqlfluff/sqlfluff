--------------------------------------
-- TPC-DS 72
--------------------------------------
SELECT i_item_desc,
               w_warehouse_name,
               d1.d_week_seq,
               Sum(CASE
                     WHEN p_promo_sk IS NULL THEN 1
                     ELSE 0
                   END) no_promo,
               Sum(CASE
                     WHEN p_promo_sk IS NOT NULL THEN 1
                     ELSE 0
                   END) promo,
               Count(*) total_cnt
FROM   catalog_sales
       JOIN inventory
         ON ( cs_item_sk = inv_item_sk )
       JOIN warehouse
         ON ( w_warehouse_sk = inv_warehouse_sk )
       JOIN item
         ON ( i_item_sk = cs_item_sk )
       JOIN customer_demographics
         ON ( cs_bill_cdemo_sk = cd_demo_sk )
       JOIN household_demographics
         ON ( cs_bill_hdemo_sk = hd_demo_sk )
       JOIN date_dim d1
         ON ( cs_sold_date_sk = d1.d_date_sk )
       JOIN date_dim d2
         ON ( inv_date_sk = d2.d_date_sk )
       JOIN date_dim d3
         ON ( cs_ship_date_sk = d3.d_date_sk )
       LEFT OUTER JOIN promotion
                    ON ( cs_promo_sk = p_promo_sk )
       LEFT OUTER JOIN catalog_returns
                    ON ( cr_item_sk = cs_item_sk
                         AND cr_order_number = cs_order_number )
WHERE  d1.d_week_seq = d2.d_week_seq
       AND inv_quantity_on_hand < cs_quantity
       AND d3.d_date > d1.d_date + INTERVAL '5' day
       AND hd_buy_potential = '501-1000'
       AND d1.d_year = 2002
       AND cd_marital_status = 'M'
GROUP  BY i_item_desc,
          w_warehouse_name,
          d1.d_week_seq
ORDER  BY total_cnt DESC,
          i_item_desc,
          w_warehouse_name,
          d_week_seq
LIMIT 100;
SELECT
  "item"."i_item_desc" AS "i_item_desc",
  "warehouse"."w_warehouse_name" AS "w_warehouse_name",
  "d1"."d_week_seq" AS "d_week_seq",
  SUM(CASE WHEN "promotion"."p_promo_sk" IS NULL THEN 1 ELSE 0 END) AS "no_promo",
  SUM(CASE WHEN NOT "promotion"."p_promo_sk" IS NULL THEN 1 ELSE 0 END) AS "promo",
  COUNT(*) AS "total_cnt"
FROM "catalog_sales" AS "catalog_sales"
JOIN "inventory" AS "inventory"
  ON "catalog_sales"."cs_item_sk" = "inventory"."inv_item_sk"
  AND "catalog_sales"."cs_quantity" > "inventory"."inv_quantity_on_hand"
JOIN "warehouse" AS "warehouse"
  ON "inventory"."inv_warehouse_sk" = "warehouse"."w_warehouse_sk"
JOIN "item" AS "item"
  ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
JOIN "customer_demographics" AS "customer_demographics"
  ON "catalog_sales"."cs_bill_cdemo_sk" = "customer_demographics"."cd_demo_sk"
  AND "customer_demographics"."cd_marital_status" = 'M'
JOIN "household_demographics" AS "household_demographics"
  ON "catalog_sales"."cs_bill_hdemo_sk" = "household_demographics"."hd_demo_sk"
  AND "household_demographics"."hd_buy_potential" = '501-1000'
JOIN "date_dim" AS "d1"
  ON "catalog_sales"."cs_sold_date_sk" = "d1"."d_date_sk" AND "d1"."d_year" = 2002
JOIN "date_dim" AS "d2"
  ON "d1"."d_week_seq" = "d2"."d_week_seq"
  AND "d2"."d_date_sk" = "inventory"."inv_date_sk"
JOIN "date_dim" AS "d3"
  ON "catalog_sales"."cs_ship_date_sk" = "d3"."d_date_sk"
  AND "d3"."d_date" > "d1"."d_date" + INTERVAL '5' DAY
LEFT JOIN "promotion" AS "promotion"
  ON "catalog_sales"."cs_promo_sk" = "promotion"."p_promo_sk"
LEFT JOIN "catalog_returns" AS "catalog_returns"
  ON "catalog_returns"."cr_item_sk" = "catalog_sales"."cs_item_sk"
  AND "catalog_returns"."cr_order_number" = "catalog_sales"."cs_order_number"
GROUP BY
  "item"."i_item_desc",
  "warehouse"."w_warehouse_name",
  "d1"."d_week_seq"
ORDER BY
  "total_cnt" DESC,
  "i_item_desc",
  "w_warehouse_name",
  "d_week_seq"
LIMIT 100;
