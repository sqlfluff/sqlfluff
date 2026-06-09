--------------------------------------
-- TPC-DS 98
--------------------------------------
SELECT i_item_id,
       i_item_desc,
       i_category,
       i_class,
       i_current_price,
       Sum(ss_ext_sales_price)                                   AS itemrevenue,
       Sum(ss_ext_sales_price) * 100 / Sum(Sum(ss_ext_sales_price))
                                         OVER (
                                           PARTITION BY i_class) AS revenueratio
FROM   store_sales,
       item,
       date_dim
WHERE  ss_item_sk = i_item_sk
       AND i_category IN ( 'Men', 'Home', 'Electronics' )
       AND ss_sold_date_sk = d_date_sk
       AND d_date BETWEEN CAST('2000-05-18' AS DATE) AND (
                          CAST('2000-05-18' AS DATE) + INTERVAL '30' DAY )
GROUP  BY i_item_id,
          i_item_desc,
          i_category,
          i_class,
          i_current_price
ORDER  BY i_category,
          i_class,
          i_item_id,
          i_item_desc,
          revenueratio;
SELECT
  "item"."i_item_id" AS "i_item_id",
  "item"."i_item_desc" AS "i_item_desc",
  "item"."i_category" AS "i_category",
  "item"."i_class" AS "i_class",
  "item"."i_current_price" AS "i_current_price",
  SUM("store_sales"."ss_ext_sales_price") AS "itemrevenue",
  SUM("store_sales"."ss_ext_sales_price") * 100 / SUM(SUM("store_sales"."ss_ext_sales_price")) OVER (PARTITION BY "item"."i_class") AS "revenueratio"
FROM "store_sales" AS "store_sales"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  AND CAST("date_dim"."d_date" AS DATE) <= CAST('2000-06-17' AS DATE)
  AND CAST("date_dim"."d_date" AS DATE) >= CAST('2000-05-18' AS DATE)
JOIN "item" AS "item"
  ON "item"."i_category" IN ('Men', 'Home', 'Electronics')
  AND "item"."i_item_sk" = "store_sales"."ss_item_sk"
GROUP BY
  "item"."i_item_id",
  "item"."i_item_desc",
  "item"."i_category",
  "item"."i_class",
  "item"."i_current_price"
ORDER BY
  "i_category",
  "i_class",
  "i_item_id",
  "i_item_desc",
  "revenueratio";
