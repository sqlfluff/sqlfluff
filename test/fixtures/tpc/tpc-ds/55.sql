--------------------------------------
-- TPC-DS 55
--------------------------------------
SELECT i_brand_id              brand_id,
               i_brand                 brand,
               Sum(ss_ext_sales_price) ext_price
FROM   date_dim,
       store_sales,
       item
WHERE  d_date_sk = ss_sold_date_sk
       AND ss_item_sk = i_item_sk
       AND i_manager_id = 33
       AND d_moy = 12
       AND d_year = 1998
GROUP  BY i_brand,
          i_brand_id
ORDER  BY ext_price DESC,
          i_brand_id
LIMIT 100;
SELECT
  "item"."i_brand_id" AS "brand_id",
  "item"."i_brand" AS "brand",
  SUM("store_sales"."ss_ext_sales_price") AS "ext_price"
FROM "date_dim" AS "date_dim"
JOIN "store_sales" AS "store_sales"
  ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "store_sales"."ss_item_sk" AND "item"."i_manager_id" = 33
WHERE
  "date_dim"."d_moy" = 12 AND "date_dim"."d_year" = 1998
GROUP BY
  "item"."i_brand",
  "item"."i_brand_id"
ORDER BY
  "ext_price" DESC,
  "brand_id"
LIMIT 100;
