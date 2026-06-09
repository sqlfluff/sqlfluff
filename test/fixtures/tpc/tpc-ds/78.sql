--------------------------------------
-- TPC-DS 78
--------------------------------------
WITH ws
     AS (SELECT d_year                 AS ws_sold_year,
                ws_item_sk,
                ws_bill_customer_sk    ws_customer_sk,
                Sum(ws_quantity)       ws_qty,
                Sum(ws_wholesale_cost) ws_wc,
                Sum(ws_sales_price)    ws_sp
         FROM   web_sales
                LEFT JOIN web_returns
                       ON wr_order_number = ws_order_number
                          AND ws_item_sk = wr_item_sk
                JOIN date_dim
                  ON ws_sold_date_sk = d_date_sk
         WHERE  wr_order_number IS NULL
         GROUP  BY d_year,
                   ws_item_sk,
                   ws_bill_customer_sk),
     cs
     AS (SELECT d_year                 AS cs_sold_year,
                cs_item_sk,
                cs_bill_customer_sk    cs_customer_sk,
                Sum(cs_quantity)       cs_qty,
                Sum(cs_wholesale_cost) cs_wc,
                Sum(cs_sales_price)    cs_sp
         FROM   catalog_sales
                LEFT JOIN catalog_returns
                       ON cr_order_number = cs_order_number
                          AND cs_item_sk = cr_item_sk
                JOIN date_dim
                  ON cs_sold_date_sk = d_date_sk
         WHERE  cr_order_number IS NULL
         GROUP  BY d_year,
                   cs_item_sk,
                   cs_bill_customer_sk),
     ss
     AS (SELECT d_year                 AS ss_sold_year,
                ss_item_sk,
                ss_customer_sk,
                Sum(ss_quantity)       ss_qty,
                Sum(ss_wholesale_cost) ss_wc,
                Sum(ss_sales_price)    ss_sp
         FROM   store_sales
                LEFT JOIN store_returns
                       ON sr_ticket_number = ss_ticket_number
                          AND ss_item_sk = sr_item_sk
                JOIN date_dim
                  ON ss_sold_date_sk = d_date_sk
         WHERE  sr_ticket_number IS NULL
         GROUP  BY d_year,
                   ss_item_sk,
                   ss_customer_sk)
SELECT ss_item_sk,
               Round(ss_qty / ( COALESCE(ws_qty + cs_qty, 1) ), 2) ratio,
               ss_qty                                              store_qty,
               ss_wc
               store_wholesale_cost,
               ss_sp
               store_sales_price,
               COALESCE(ws_qty, 0) + COALESCE(cs_qty, 0)
               other_chan_qty,
               COALESCE(ws_wc, 0) + COALESCE(cs_wc, 0)
               other_chan_wholesale_cost,
               COALESCE(ws_sp, 0) + COALESCE(cs_sp, 0)
               other_chan_sales_price
FROM   ss
       LEFT JOIN ws
              ON ( ws_sold_year = ss_sold_year
                   AND ws_item_sk = ss_item_sk
                   AND ws_customer_sk = ss_customer_sk )
       LEFT JOIN cs
              ON ( cs_sold_year = ss_sold_year
                   AND cs_item_sk = cs_item_sk
                   AND cs_customer_sk = ss_customer_sk )
WHERE  COALESCE(ws_qty, 0) > 0
       AND COALESCE(cs_qty, 0) > 0
       AND ss_sold_year = 1999
ORDER  BY ss_item_sk,
          ss_qty DESC,
          ss_wc DESC,
          ss_sp DESC,
          other_chan_qty,
          other_chan_wholesale_cost,
          other_chan_sales_price,
          Round(ss_qty / ( COALESCE(ws_qty + cs_qty, 1) ), 2)
LIMIT 100;
WITH "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year"
  FROM "date_dim" AS "date_dim"
), "ws" AS (
  SELECT
    "date_dim"."d_year" AS "ws_sold_year",
    "web_sales"."ws_item_sk" AS "ws_item_sk",
    "web_sales"."ws_bill_customer_sk" AS "ws_customer_sk",
    SUM("web_sales"."ws_quantity") AS "ws_qty",
    SUM("web_sales"."ws_wholesale_cost") AS "ws_wc",
    SUM("web_sales"."ws_sales_price") AS "ws_sp"
  FROM "web_sales" AS "web_sales"
  LEFT JOIN "web_returns" AS "web_returns"
    ON "web_returns"."wr_item_sk" = "web_sales"."ws_item_sk"
    AND "web_returns"."wr_order_number" = "web_sales"."ws_order_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  WHERE
    "web_returns"."wr_order_number" IS NULL
  GROUP BY
    "date_dim"."d_year",
    "web_sales"."ws_item_sk",
    "web_sales"."ws_bill_customer_sk"
), "cs" AS (
  SELECT
    "date_dim"."d_year" AS "cs_sold_year",
    "catalog_sales"."cs_item_sk" AS "cs_item_sk",
    "catalog_sales"."cs_bill_customer_sk" AS "cs_customer_sk",
    SUM("catalog_sales"."cs_quantity") AS "cs_qty",
    SUM("catalog_sales"."cs_wholesale_cost") AS "cs_wc",
    SUM("catalog_sales"."cs_sales_price") AS "cs_sp"
  FROM "catalog_sales" AS "catalog_sales"
  LEFT JOIN "catalog_returns" AS "catalog_returns"
    ON "catalog_returns"."cr_item_sk" = "catalog_sales"."cs_item_sk"
    AND "catalog_returns"."cr_order_number" = "catalog_sales"."cs_order_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  WHERE
    "catalog_returns"."cr_order_number" IS NULL
  GROUP BY
    "date_dim"."d_year",
    "catalog_sales"."cs_item_sk",
    "catalog_sales"."cs_bill_customer_sk"
), "ss" AS (
  SELECT
    "date_dim"."d_year" AS "ss_sold_year",
    "store_sales"."ss_item_sk" AS "ss_item_sk",
    "store_sales"."ss_customer_sk" AS "ss_customer_sk",
    SUM("store_sales"."ss_quantity") AS "ss_qty",
    SUM("store_sales"."ss_wholesale_cost") AS "ss_wc",
    SUM("store_sales"."ss_sales_price") AS "ss_sp"
  FROM "store_sales" AS "store_sales"
  LEFT JOIN "store_returns" AS "store_returns"
    ON "store_returns"."sr_item_sk" = "store_sales"."ss_item_sk"
    AND "store_returns"."sr_ticket_number" = "store_sales"."ss_ticket_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  WHERE
    "store_returns"."sr_ticket_number" IS NULL
  GROUP BY
    "date_dim"."d_year",
    "store_sales"."ss_item_sk",
    "store_sales"."ss_customer_sk"
)
SELECT
  "ss"."ss_item_sk" AS "ss_item_sk",
  ROUND("ss"."ss_qty" / COALESCE("ws"."ws_qty" + "cs"."cs_qty", 1), 2) AS "ratio",
  "ss"."ss_qty" AS "store_qty",
  "ss"."ss_wc" AS "store_wholesale_cost",
  "ss"."ss_sp" AS "store_sales_price",
  COALESCE("ws"."ws_qty", 0) + COALESCE("cs"."cs_qty", 0) AS "other_chan_qty",
  COALESCE("ws"."ws_wc", 0) + COALESCE("cs"."cs_wc", 0) AS "other_chan_wholesale_cost",
  COALESCE("ws"."ws_sp", 0) + COALESCE("cs"."cs_sp", 0) AS "other_chan_sales_price"
FROM "ss" AS "ss"
LEFT JOIN "ws" AS "ws"
  ON "ss"."ss_customer_sk" = "ws"."ws_customer_sk"
  AND "ss"."ss_item_sk" = "ws"."ws_item_sk"
  AND "ss"."ss_sold_year" = "ws"."ws_sold_year"
LEFT JOIN "cs" AS "cs"
  ON "cs"."cs_customer_sk" = "ss"."ss_customer_sk"
  AND "cs"."cs_item_sk" = "cs"."cs_item_sk"
  AND "cs"."cs_sold_year" = "ss"."ss_sold_year"
WHERE
  "ss"."ss_sold_year" = 1999
  AND COALESCE("cs"."cs_qty", 0) > 0
  AND COALESCE("ws"."ws_qty", 0) > 0
ORDER BY
  "ss_item_sk",
  "ss"."ss_qty" DESC,
  "ss"."ss_wc" DESC,
  "ss"."ss_sp" DESC,
  "other_chan_qty",
  "other_chan_wholesale_cost",
  "other_chan_sales_price",
  ROUND("ss"."ss_qty" / COALESCE("ws"."ws_qty" + "cs"."cs_qty", 1), 2)
LIMIT 100;
