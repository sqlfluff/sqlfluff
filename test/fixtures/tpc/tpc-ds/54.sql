--------------------------------------
-- TPC-DS 54
--------------------------------------
WITH my_customers
     AS (SELECT DISTINCT c_customer_sk,
                         c_current_addr_sk
         FROM   (SELECT cs_sold_date_sk     sold_date_sk,
                        cs_bill_customer_sk customer_sk,
                        cs_item_sk          item_sk
                 FROM   catalog_sales
                 UNION ALL
                 SELECT ws_sold_date_sk     sold_date_sk,
                        ws_bill_customer_sk customer_sk,
                        ws_item_sk          item_sk
                 FROM   web_sales) cs_or_ws_sales,
                item,
                date_dim,
                customer
         WHERE  sold_date_sk = d_date_sk
                AND item_sk = i_item_sk
                AND i_category = 'Sports'
                AND i_class = 'fitness'
                AND c_customer_sk = cs_or_ws_sales.customer_sk
                AND d_moy = 5
                AND d_year = 2000),
     my_revenue
     AS (SELECT c_customer_sk,
                Sum(ss_ext_sales_price) AS revenue
         FROM   my_customers,
                store_sales,
                customer_address,
                store,
                date_dim
         WHERE  c_current_addr_sk = ca_address_sk
                AND ca_county = s_county
                AND ca_state = s_state
                AND ss_sold_date_sk = d_date_sk
                AND c_customer_sk = ss_customer_sk
                AND d_month_seq BETWEEN (SELECT DISTINCT d_month_seq + 1
                                         FROM   date_dim
                                         WHERE  d_year = 2000
                                                AND d_moy = 5) AND
                                        (SELECT DISTINCT
                                        d_month_seq + 3
                                         FROM   date_dim
                                         WHERE  d_year = 2000
                                                AND d_moy = 5)
         GROUP  BY c_customer_sk),
     segments
     AS (SELECT Cast(( revenue / 50 ) AS INT) AS segment
         FROM   my_revenue)
SELECT segment,
               Count(*)     AS num_customers,
               segment * 50 AS segment_base
FROM   segments
GROUP  BY segment
ORDER  BY segment,
          num_customers
LIMIT 100;
WITH "cs_or_ws_sales" AS (
  SELECT
    "catalog_sales"."cs_sold_date_sk" AS "sold_date_sk",
    "catalog_sales"."cs_bill_customer_sk" AS "customer_sk",
    "catalog_sales"."cs_item_sk" AS "item_sk"
  FROM "catalog_sales" AS "catalog_sales"
  UNION ALL
  SELECT
    "web_sales"."ws_sold_date_sk" AS "sold_date_sk",
    "web_sales"."ws_bill_customer_sk" AS "customer_sk",
    "web_sales"."ws_item_sk" AS "item_sk"
  FROM "web_sales" AS "web_sales"
), "my_customers" AS (
  SELECT DISTINCT
    "customer"."c_customer_sk" AS "c_customer_sk",
    "customer"."c_current_addr_sk" AS "c_current_addr_sk"
  FROM "cs_or_ws_sales" AS "cs_or_ws_sales"
  JOIN "customer" AS "customer"
    ON "cs_or_ws_sales"."customer_sk" = "customer"."c_customer_sk"
  JOIN "date_dim" AS "date_dim"
    ON "cs_or_ws_sales"."sold_date_sk" = "date_dim"."d_date_sk"
    AND "date_dim"."d_moy" = 5
    AND "date_dim"."d_year" = 2000
  JOIN "item" AS "item"
    ON "cs_or_ws_sales"."item_sk" = "item"."i_item_sk"
    AND "item"."i_category" = 'Sports'
    AND "item"."i_class" = 'fitness'
), "_u_0" AS (
  SELECT DISTINCT
    "date_dim"."d_month_seq" + 1 AS "_col_0"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_moy" = 5 AND "date_dim"."d_year" = 2000
), "_u_1" AS (
  SELECT DISTINCT
    "date_dim"."d_month_seq" + 3 AS "_col_0"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_moy" = 5 AND "date_dim"."d_year" = 2000
), "my_revenue" AS (
  SELECT
    SUM("store_sales"."ss_ext_sales_price") AS "revenue"
  FROM "my_customers" AS "my_customers"
  JOIN "customer_address" AS "customer_address"
    ON "customer_address"."ca_address_sk" = "my_customers"."c_current_addr_sk"
  JOIN "store_sales" AS "store_sales"
    ON "my_customers"."c_customer_sk" = "store_sales"."ss_customer_sk"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  JOIN "store" AS "store"
    ON "customer_address"."ca_county" = "store"."s_county"
    AND "customer_address"."ca_state" = "store"."s_state"
  JOIN "_u_0" AS "_u_0"
    ON "_u_0"."_col_0" <= "date_dim"."d_month_seq"
  JOIN "_u_1" AS "_u_1"
    ON "_u_1"."_col_0" >= "date_dim"."d_month_seq"
  GROUP BY
    "my_customers"."c_customer_sk"
)
SELECT
  CAST((
    "my_revenue"."revenue" / 50
  ) AS INT) AS "segment",
  COUNT(*) AS "num_customers",
  CAST((
    "my_revenue"."revenue" / 50
  ) AS INT) * 50 AS "segment_base"
FROM "my_revenue" AS "my_revenue"
GROUP BY
  CAST((
    "my_revenue"."revenue" / 50
  ) AS INT)
ORDER BY
  "segment",
  "num_customers"
LIMIT 100;
