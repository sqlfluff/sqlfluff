--------------------------------------
-- TPC-DS 29
--------------------------------------
SELECT i_item_id,
               i_item_desc,
               s_store_id,
               s_store_name,
               Avg(ss_quantity)        AS store_sales_quantity,
               Avg(sr_return_quantity) AS store_returns_quantity,
               Avg(cs_quantity)        AS catalog_sales_quantity
FROM   store_sales,
       store_returns,
       catalog_sales,
       date_dim d1,
       date_dim d2,
       date_dim d3,
       store,
       item
WHERE  d1.d_moy = 4
       AND d1.d_year = 1998
       AND d1.d_date_sk = ss_sold_date_sk
       AND i_item_sk = ss_item_sk
       AND s_store_sk = ss_store_sk
       AND ss_customer_sk = sr_customer_sk
       AND ss_item_sk = sr_item_sk
       AND ss_ticket_number = sr_ticket_number
       AND sr_returned_date_sk = d2.d_date_sk
       AND d2.d_moy BETWEEN 4 AND 4 + 3
       AND d2.d_year = 1998
       AND sr_customer_sk = cs_bill_customer_sk
       AND sr_item_sk = cs_item_sk
       AND cs_sold_date_sk = d3.d_date_sk
       AND d3.d_year IN ( 1998, 1998 + 1, 1998 + 2 )
GROUP  BY i_item_id,
          i_item_desc,
          s_store_id,
          s_store_name
ORDER  BY i_item_id,
          i_item_desc,
          s_store_id,
          s_store_name
LIMIT 100;
SELECT
  "item"."i_item_id" AS "i_item_id",
  "item"."i_item_desc" AS "i_item_desc",
  "store"."s_store_id" AS "s_store_id",
  "store"."s_store_name" AS "s_store_name",
  AVG("store_sales"."ss_quantity") AS "store_sales_quantity",
  AVG("store_returns"."sr_return_quantity") AS "store_returns_quantity",
  AVG("catalog_sales"."cs_quantity") AS "catalog_sales_quantity"
FROM "store_sales" AS "store_sales"
JOIN "date_dim" AS "d1"
  ON "d1"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  AND "d1"."d_moy" = 4
  AND "d1"."d_year" = 1998
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
JOIN "store" AS "store"
  ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
JOIN "store_returns" AS "store_returns"
  ON "store_returns"."sr_customer_sk" = "store_sales"."ss_customer_sk"
  AND "store_returns"."sr_item_sk" = "store_sales"."ss_item_sk"
  AND "store_returns"."sr_ticket_number" = "store_sales"."ss_ticket_number"
JOIN "catalog_sales" AS "catalog_sales"
  ON "catalog_sales"."cs_bill_customer_sk" = "store_returns"."sr_customer_sk"
  AND "catalog_sales"."cs_item_sk" = "store_returns"."sr_item_sk"
JOIN "date_dim" AS "d2"
  ON "d2"."d_date_sk" = "store_returns"."sr_returned_date_sk"
  AND "d2"."d_moy" <= 7
  AND "d2"."d_moy" >= 4
  AND "d2"."d_year" = 1998
JOIN "date_dim" AS "d3"
  ON "catalog_sales"."cs_sold_date_sk" = "d3"."d_date_sk"
  AND "d3"."d_year" IN (1998, 1999, 2000)
GROUP BY
  "item"."i_item_id",
  "item"."i_item_desc",
  "store"."s_store_id",
  "store"."s_store_name"
ORDER BY
  "i_item_id",
  "i_item_desc",
  "s_store_id",
  "s_store_name"
LIMIT 100;
