--------------------------------------
-- TPC-DS 42
--------------------------------------
SELECT dt.d_year,
               item.i_category_id,
               item.i_category,
               Sum(ss_ext_sales_price) AS "_col_3"
FROM   date_dim dt,
       store_sales,
       item
WHERE  dt.d_date_sk = store_sales.ss_sold_date_sk
       AND store_sales.ss_item_sk = item.i_item_sk
       AND item.i_manager_id = 1
       AND dt.d_moy = 12
       AND dt.d_year = 2000
GROUP  BY dt.d_year,
          item.i_category_id,
          item.i_category
ORDER  BY Sum(ss_ext_sales_price) DESC,
          dt.d_year,
          item.i_category_id,
          item.i_category
LIMIT 100;
SELECT
  "dt"."d_year" AS "d_year",
  "item"."i_category_id" AS "i_category_id",
  "item"."i_category" AS "i_category",
  SUM("store_sales"."ss_ext_sales_price") AS "_col_3"
FROM "date_dim" AS "dt"
JOIN "store_sales" AS "store_sales"
  ON "dt"."d_date_sk" = "store_sales"."ss_sold_date_sk"
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "store_sales"."ss_item_sk" AND "item"."i_manager_id" = 1
WHERE
  "dt"."d_moy" = 12 AND "dt"."d_year" = 2000
GROUP BY
  "dt"."d_year",
  "item"."i_category_id",
  "item"."i_category"
ORDER BY
  "_col_3" DESC,
  "d_year",
  "i_category_id",
  "i_category"
LIMIT 100;
