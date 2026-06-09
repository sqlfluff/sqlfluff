--------------------------------------
-- TPC-DS 12
--------------------------------------
SELECT
         i_item_id ,
         i_item_desc ,
         i_category ,
         i_class ,
         i_current_price ,
         Sum(ws_ext_sales_price)                                                              AS itemrevenue ,
         Sum(ws_ext_sales_price)*100/Sum(Sum(ws_ext_sales_price)) OVER (partition BY i_class) AS revenueratio
FROM     web_sales ,
         item ,
         date_dim
WHERE    ws_item_sk = i_item_sk
AND      i_category IN ('Home',
                        'Men',
                        'Women')
AND      ws_sold_date_sk = d_date_sk
AND      d_date BETWEEN Cast('2000-05-11' AS DATE) AND      (
                  Cast('2000-05-11' AS DATE) + INTERVAL '30' day)
GROUP BY i_item_id ,
         i_item_desc ,
         i_category ,
         i_class ,
         i_current_price
ORDER BY i_category ,
         i_class ,
         i_item_id ,
         i_item_desc ,
         revenueratio
LIMIT 100;
SELECT
  "item"."i_item_id" AS "i_item_id",
  "item"."i_item_desc" AS "i_item_desc",
  "item"."i_category" AS "i_category",
  "item"."i_class" AS "i_class",
  "item"."i_current_price" AS "i_current_price",
  SUM("web_sales"."ws_ext_sales_price") AS "itemrevenue",
  SUM("web_sales"."ws_ext_sales_price") * 100 / SUM(SUM("web_sales"."ws_ext_sales_price")) OVER (PARTITION BY "item"."i_class") AS "revenueratio"
FROM "web_sales" AS "web_sales"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  AND CAST("date_dim"."d_date" AS DATE) <= CAST('2000-06-10' AS DATE)
  AND CAST("date_dim"."d_date" AS DATE) >= CAST('2000-05-11' AS DATE)
JOIN "item" AS "item"
  ON "item"."i_category" IN ('Home', 'Men', 'Women')
  AND "item"."i_item_sk" = "web_sales"."ws_item_sk"
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
  "revenueratio"
LIMIT 100;
