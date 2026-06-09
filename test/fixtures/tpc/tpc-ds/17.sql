--------------------------------------
-- TPC-DS 17
--------------------------------------
SELECT i_item_id,
               i_item_desc,
               s_state,
               Count(ss_quantity)                                        AS
               store_sales_quantitycount,
               Avg(ss_quantity)                                          AS
               store_sales_quantityave,
               Stddev_samp(ss_quantity)                                  AS
               store_sales_quantitystdev,
               Stddev_samp(ss_quantity) / Avg(ss_quantity)               AS
               store_sales_quantitycov,
               Count(sr_return_quantity)                                 AS
               store_returns_quantitycount,
               Avg(sr_return_quantity)                                   AS
               store_returns_quantityave,
               Stddev_samp(sr_return_quantity)                           AS
               store_returns_quantitystdev,
               Stddev_samp(sr_return_quantity) / Avg(sr_return_quantity) AS
               store_returns_quantitycov,
               Count(cs_quantity)                                        AS
               catalog_sales_quantitycount,
               Avg(cs_quantity)                                          AS
               catalog_sales_quantityave,
               Stddev_samp(cs_quantity) / Avg(cs_quantity)               AS
               catalog_sales_quantitystdev,
               Stddev_samp(cs_quantity) / Avg(cs_quantity)               AS
               catalog_sales_quantitycov
FROM   store_sales,
       store_returns,
       catalog_sales,
       date_dim d1,
       date_dim d2,
       date_dim d3,
       store,
       item
WHERE  d1.d_quarter_name = '1999Q1'
       AND d1.d_date_sk = ss_sold_date_sk
       AND i_item_sk = ss_item_sk
       AND s_store_sk = ss_store_sk
       AND ss_customer_sk = sr_customer_sk
       AND ss_item_sk = sr_item_sk
       AND ss_ticket_number = sr_ticket_number
       AND sr_returned_date_sk = d2.d_date_sk
       AND d2.d_quarter_name IN ( '1999Q1', '1999Q2', '1999Q3' )
       AND sr_customer_sk = cs_bill_customer_sk
       AND sr_item_sk = cs_item_sk
       AND cs_sold_date_sk = d3.d_date_sk
       AND d3.d_quarter_name IN ( '1999Q1', '1999Q2', '1999Q3' )
GROUP  BY i_item_id,
          i_item_desc,
          s_state
ORDER  BY i_item_id,
          i_item_desc,
          s_state
LIMIT 100;
SELECT
  "item"."i_item_id" AS "i_item_id",
  "item"."i_item_desc" AS "i_item_desc",
  "store"."s_state" AS "s_state",
  COUNT("store_sales"."ss_quantity") AS "store_sales_quantitycount",
  AVG("store_sales"."ss_quantity") AS "store_sales_quantityave",
  STDDEV_SAMP("store_sales"."ss_quantity") AS "store_sales_quantitystdev",
  STDDEV_SAMP("store_sales"."ss_quantity") / AVG("store_sales"."ss_quantity") AS "store_sales_quantitycov",
  COUNT("store_returns"."sr_return_quantity") AS "store_returns_quantitycount",
  AVG("store_returns"."sr_return_quantity") AS "store_returns_quantityave",
  STDDEV_SAMP("store_returns"."sr_return_quantity") AS "store_returns_quantitystdev",
  STDDEV_SAMP("store_returns"."sr_return_quantity") / AVG("store_returns"."sr_return_quantity") AS "store_returns_quantitycov",
  COUNT("catalog_sales"."cs_quantity") AS "catalog_sales_quantitycount",
  AVG("catalog_sales"."cs_quantity") AS "catalog_sales_quantityave",
  STDDEV_SAMP("catalog_sales"."cs_quantity") / AVG("catalog_sales"."cs_quantity") AS "catalog_sales_quantitystdev",
  STDDEV_SAMP("catalog_sales"."cs_quantity") / AVG("catalog_sales"."cs_quantity") AS "catalog_sales_quantitycov"
FROM "store_sales" AS "store_sales"
JOIN "date_dim" AS "d1"
  ON "d1"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  AND "d1"."d_quarter_name" = '1999Q1'
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
  AND "d2"."d_quarter_name" IN ('1999Q1', '1999Q2', '1999Q3')
JOIN "date_dim" AS "d3"
  ON "catalog_sales"."cs_sold_date_sk" = "d3"."d_date_sk"
  AND "d3"."d_quarter_name" IN ('1999Q1', '1999Q2', '1999Q3')
GROUP BY
  "item"."i_item_id",
  "item"."i_item_desc",
  "store"."s_state"
ORDER BY
  "i_item_id",
  "i_item_desc",
  "s_state"
LIMIT 100;
