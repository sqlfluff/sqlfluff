--------------------------------------
-- TPC-DS 19
--------------------------------------
SELECT i_brand_id              brand_id,
               i_brand                 brand,
               i_manufact_id,
               i_manufact,
               Sum(ss_ext_sales_price) ext_price
FROM   date_dim,
       store_sales,
       item,
       customer,
       customer_address,
       store
WHERE  d_date_sk = ss_sold_date_sk
       AND ss_item_sk = i_item_sk
       AND i_manager_id = 38
       AND d_moy = 12
       AND d_year = 1998
       AND ss_customer_sk = c_customer_sk
       AND c_current_addr_sk = ca_address_sk
       AND SUBSTRING(ca_zip, 1, 5) <> SUBSTRING(s_zip, 1, 5)
       AND ss_store_sk = s_store_sk
GROUP  BY i_brand,
          i_brand_id,
          i_manufact_id,
          i_manufact
ORDER  BY ext_price DESC,
          i_brand,
          i_brand_id,
          i_manufact_id,
          i_manufact
LIMIT 100;
SELECT
  "item"."i_brand_id" AS "brand_id",
  "item"."i_brand" AS "brand",
  "item"."i_manufact_id" AS "i_manufact_id",
  "item"."i_manufact" AS "i_manufact",
  SUM("store_sales"."ss_ext_sales_price") AS "ext_price"
FROM "date_dim" AS "date_dim"
JOIN "store_sales" AS "store_sales"
  ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
JOIN "customer" AS "customer"
  ON "customer"."c_customer_sk" = "store_sales"."ss_customer_sk"
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "store_sales"."ss_item_sk" AND "item"."i_manager_id" = 38
JOIN "customer_address" AS "customer_address"
  ON "customer"."c_current_addr_sk" = "customer_address"."ca_address_sk"
JOIN "store" AS "store"
  ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
  AND SUBSTRING("customer_address"."ca_zip", 1, 5) <> SUBSTRING("store"."s_zip", 1, 5)
WHERE
  "date_dim"."d_moy" = 12 AND "date_dim"."d_year" = 1998
GROUP BY
  "item"."i_brand",
  "item"."i_brand_id",
  "item"."i_manufact_id",
  "item"."i_manufact"
ORDER BY
  "ext_price" DESC,
  "brand",
  "brand_id",
  "i_manufact_id",
  "i_manufact"
LIMIT 100;
