--------------------------------------
-- TPC-DS 23
--------------------------------------
WITH frequent_ss_items
     AS (SELECT SUBSTRING(i_item_desc, 1, 30) itemdesc,
                i_item_sk                  item_sk,
                d_date                     solddate,
                Count(*)                   cnt
         FROM   store_sales,
                date_dim,
                item
         WHERE  ss_sold_date_sk = d_date_sk
                AND ss_item_sk = i_item_sk
                AND d_year IN ( 1998, 1998 + 1, 1998 + 2, 1998 + 3 )
         GROUP  BY SUBSTRING(i_item_desc, 1, 30),
                   i_item_sk,
                   d_date
         HAVING Count(*) > 4),
     max_store_sales
     AS (SELECT Max(csales) tpcds_cmax
         FROM   (SELECT c_customer_sk,
                        Sum(ss_quantity * ss_sales_price) csales
                 FROM   store_sales,
                        customer,
                        date_dim
                 WHERE  ss_customer_sk = c_customer_sk
                        AND ss_sold_date_sk = d_date_sk
                        AND d_year IN ( 1998, 1998 + 1, 1998 + 2, 1998 + 3 )
                 GROUP  BY c_customer_sk)),
     best_ss_customer
     AS (SELECT c_customer_sk,
                Sum(ss_quantity * ss_sales_price) ssales
         FROM   store_sales,
                customer
         WHERE  ss_customer_sk = c_customer_sk
         GROUP  BY c_customer_sk
         HAVING Sum(ss_quantity * ss_sales_price) >
                ( 95 / 100.0 ) * (SELECT *
                                  FROM   max_store_sales))
SELECT Sum(sales) AS "_col_0"
FROM   (SELECT cs_quantity * cs_list_price sales
        FROM   catalog_sales,
               date_dim
        WHERE  d_year = 1998
               AND d_moy = 6
               AND cs_sold_date_sk = d_date_sk
               AND cs_item_sk IN (SELECT item_sk
                                  FROM   frequent_ss_items)
               AND cs_bill_customer_sk IN (SELECT c_customer_sk
                                           FROM   best_ss_customer)
        UNION ALL
        SELECT ws_quantity * ws_list_price sales
        FROM   web_sales,
               date_dim
        WHERE  d_year = 1998
               AND d_moy = 6
               AND ws_sold_date_sk = d_date_sk
               AND ws_item_sk IN (SELECT item_sk
                                  FROM   frequent_ss_items)
               AND ws_bill_customer_sk IN (SELECT c_customer_sk
                                           FROM   best_ss_customer)) LIMIT 100;
WITH "frequent_ss_items" AS (
  SELECT
    "item"."i_item_sk" AS "item_sk"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
    AND "date_dim"."d_year" IN (1998, 1999, 2000, 2001)
  JOIN "item" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  GROUP BY
    SUBSTRING("item"."i_item_desc", 1, 30),
    "item"."i_item_sk",
    "date_dim"."d_date"
  HAVING
    COUNT(*) > 4
), "customer_2" AS (
  SELECT
    "customer"."c_customer_sk" AS "c_customer_sk"
  FROM "customer" AS "customer"
), "_0" AS (
  SELECT
    SUM("store_sales"."ss_quantity" * "store_sales"."ss_sales_price") AS "csales"
  FROM "store_sales" AS "store_sales"
  JOIN "customer_2" AS "customer"
    ON "customer"."c_customer_sk" = "store_sales"."ss_customer_sk"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
    AND "date_dim"."d_year" IN (1998, 1999, 2000, 2001)
  GROUP BY
    "customer"."c_customer_sk"
), "max_store_sales" AS (
  SELECT
    MAX("_0"."csales") AS "tpcds_cmax"
  FROM "_0" AS "_0"
), "best_ss_customer" AS (
  SELECT
    "customer"."c_customer_sk" AS "c_customer_sk"
  FROM "store_sales" AS "store_sales"
  CROSS JOIN "max_store_sales" AS "max_store_sales"
  JOIN "customer_2" AS "customer"
    ON "customer"."c_customer_sk" = "store_sales"."ss_customer_sk"
  GROUP BY
    "customer"."c_customer_sk"
  HAVING
    0.95 * MAX("max_store_sales"."tpcds_cmax") < SUM("store_sales"."ss_quantity" * "store_sales"."ss_sales_price")
), "date_dim_4" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year",
    "date_dim"."d_moy" AS "d_moy"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_moy" = 6 AND "date_dim"."d_year" = 1998
), "_u_1" AS (
  SELECT
    "frequent_ss_items"."item_sk" AS "item_sk"
  FROM "frequent_ss_items" AS "frequent_ss_items"
  GROUP BY
    "frequent_ss_items"."item_sk"
), "_u_2" AS (
  SELECT
    "best_ss_customer"."c_customer_sk" AS "c_customer_sk"
  FROM "best_ss_customer" AS "best_ss_customer"
  GROUP BY
    "best_ss_customer"."c_customer_sk"
), "_1" AS (
  SELECT
    "catalog_sales"."cs_quantity" * "catalog_sales"."cs_list_price" AS "sales"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "date_dim_4" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  LEFT JOIN "_u_1" AS "_u_1"
    ON "_u_1"."item_sk" = "catalog_sales"."cs_item_sk"
  LEFT JOIN "_u_2" AS "_u_2"
    ON "_u_2"."c_customer_sk" = "catalog_sales"."cs_bill_customer_sk"
  WHERE
    NOT "_u_1"."item_sk" IS NULL AND NOT "_u_2"."c_customer_sk" IS NULL
  UNION ALL
  SELECT
    "web_sales"."ws_quantity" * "web_sales"."ws_list_price" AS "sales"
  FROM "web_sales" AS "web_sales"
  JOIN "date_dim_4" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  LEFT JOIN "_u_1" AS "_u_3"
    ON "_u_3"."item_sk" = "web_sales"."ws_item_sk"
  LEFT JOIN "_u_2" AS "_u_4"
    ON "_u_4"."c_customer_sk" = "web_sales"."ws_bill_customer_sk"
  WHERE
    NOT "_u_3"."item_sk" IS NULL AND NOT "_u_4"."c_customer_sk" IS NULL
)
SELECT
  SUM("_1"."sales") AS "_col_0"
FROM "_1" AS "_1"
LIMIT 100;
