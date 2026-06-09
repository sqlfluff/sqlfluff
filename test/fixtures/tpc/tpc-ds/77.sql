--------------------------------------
-- TPC-DS 77
--------------------------------------
WITH ss AS
(
         SELECT   s_store_sk,
                  Sum(ss_ext_sales_price) AS sales,
                  Sum(ss_net_profit)      AS profit
         FROM     store_sales,
                  date_dim,
                  store
         WHERE    ss_sold_date_sk = d_date_sk
         AND      d_date BETWEEN Cast('2001-08-16' AS DATE) AND      (
                           Cast('2001-08-16' AS DATE) + INTERVAL '30' day)
         AND      ss_store_sk = s_store_sk
         GROUP BY s_store_sk) , sr AS
(
         SELECT   s_store_sk,
                  sum(sr_return_amt) AS returns1,
                  sum(sr_net_loss)   AS profit_loss
         FROM     store_returns,
                  date_dim,
                  store
         WHERE    sr_returned_date_sk = d_date_sk
         AND      d_date BETWEEN cast('2001-08-16' AS date) AND      (
                           cast('2001-08-16' AS date) + INTERVAL '30' day)
         AND      sr_store_sk = s_store_sk
         GROUP BY s_store_sk), cs AS
(
         SELECT   cs_call_center_sk,
                  sum(cs_ext_sales_price) AS sales,
                  sum(cs_net_profit)      AS profit
         FROM     catalog_sales,
                  date_dim
         WHERE    cs_sold_date_sk = d_date_sk
         AND      d_date BETWEEN cast('2001-08-16' AS date) AND      (
                           cast('2001-08-16' AS date) + INTERVAL '30' day)
         GROUP BY cs_call_center_sk ), cr AS
(
         SELECT   cr_call_center_sk,
                  sum(cr_return_amount) AS returns1,
                  sum(cr_net_loss)      AS profit_loss
         FROM     catalog_returns,
                  date_dim
         WHERE    cr_returned_date_sk = d_date_sk
         AND      d_date BETWEEN cast('2001-08-16' AS date) AND      (
                           cast('2001-08-16' AS date) + INTERVAL '30' day)
         GROUP BY cr_call_center_sk ), ws AS
(
         SELECT   wp_web_page_sk,
                  sum(ws_ext_sales_price) AS sales,
                  sum(ws_net_profit)      AS profit
         FROM     web_sales,
                  date_dim,
                  web_page
         WHERE    ws_sold_date_sk = d_date_sk
         AND      d_date BETWEEN cast('2001-08-16' AS date) AND      (
                           cast('2001-08-16' AS date) + INTERVAL '30' day)
         AND      ws_web_page_sk = wp_web_page_sk
         GROUP BY wp_web_page_sk), wr AS
(
         SELECT   wp_web_page_sk,
                  sum(wr_return_amt) AS returns1,
                  sum(wr_net_loss)   AS profit_loss
         FROM     web_returns,
                  date_dim,
                  web_page
         WHERE    wr_returned_date_sk = d_date_sk
         AND      d_date BETWEEN cast('2001-08-16' AS date) AND      (
                           cast('2001-08-16' AS date) + INTERVAL '30' day)
         AND      wr_web_page_sk = wp_web_page_sk
         GROUP BY wp_web_page_sk)
SELECT
         channel ,
         id ,
         sum(sales)   AS sales ,
         sum(returns1) AS returns1 ,
         sum(profit)  AS profit
FROM     (
                   SELECT    'store channel' AS channel ,
                             ss.s_store_sk   AS id ,
                             sales ,
                             COALESCE(returns1, 0)               AS returns1 ,
                             (profit - COALESCE(profit_loss,0)) AS profit
                   FROM      ss
                   LEFT JOIN sr
                   ON        ss.s_store_sk = sr.s_store_sk
                   UNION ALL
                   SELECT 'catalog channel' AS channel ,
                          cs_call_center_sk AS id ,
                          sales ,
                          returns1 ,
                          (profit - profit_loss) AS profit
                   FROM   cs ,
                          cr
                   UNION ALL
                   SELECT    'web channel'     AS channel ,
                             ws.wp_web_page_sk AS id ,
                             sales ,
                             COALESCE(returns1, 0)                  returns1 ,
                             (profit - COALESCE(profit_loss,0)) AS profit
                   FROM      ws
                   LEFT JOIN wr
                   ON        ws.wp_web_page_sk = wr.wp_web_page_sk ) x
GROUP BY rollup (channel, id)
ORDER BY channel ,
         id
LIMIT 100;
WITH "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_date" AS "d_date"
  FROM "date_dim" AS "date_dim"
  WHERE
    CAST("date_dim"."d_date" AS DATE) <= CAST('2001-09-15' AS DATE)
    AND CAST("date_dim"."d_date" AS DATE) >= CAST('2001-08-16' AS DATE)
), "store_2" AS (
  SELECT
    "store"."s_store_sk" AS "s_store_sk"
  FROM "store" AS "store"
), "ss" AS (
  SELECT
    "store"."s_store_sk" AS "s_store_sk",
    SUM("store_sales"."ss_ext_sales_price") AS "sales",
    SUM("store_sales"."ss_net_profit") AS "profit"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  JOIN "store_2" AS "store"
    ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
  GROUP BY
    "store"."s_store_sk"
), "sr" AS (
  SELECT
    "store"."s_store_sk" AS "s_store_sk",
    SUM("store_returns"."sr_return_amt") AS "returns1",
    SUM("store_returns"."sr_net_loss") AS "profit_loss"
  FROM "store_returns" AS "store_returns"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_returns"."sr_returned_date_sk"
  JOIN "store_2" AS "store"
    ON "store"."s_store_sk" = "store_returns"."sr_store_sk"
  GROUP BY
    "store"."s_store_sk"
), "cs" AS (
  SELECT
    "catalog_sales"."cs_call_center_sk" AS "cs_call_center_sk",
    SUM("catalog_sales"."cs_ext_sales_price") AS "sales",
    SUM("catalog_sales"."cs_net_profit") AS "profit"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  GROUP BY
    "catalog_sales"."cs_call_center_sk"
), "cr" AS (
  SELECT
    SUM("catalog_returns"."cr_return_amount") AS "returns1",
    SUM("catalog_returns"."cr_net_loss") AS "profit_loss"
  FROM "catalog_returns" AS "catalog_returns"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_returns"."cr_returned_date_sk" = "date_dim"."d_date_sk"
  GROUP BY
    "catalog_returns"."cr_call_center_sk"
), "web_page_2" AS (
  SELECT
    "web_page"."wp_web_page_sk" AS "wp_web_page_sk"
  FROM "web_page" AS "web_page"
), "ws" AS (
  SELECT
    "web_page"."wp_web_page_sk" AS "wp_web_page_sk",
    SUM("web_sales"."ws_ext_sales_price") AS "sales",
    SUM("web_sales"."ws_net_profit") AS "profit"
  FROM "web_sales" AS "web_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  JOIN "web_page_2" AS "web_page"
    ON "web_page"."wp_web_page_sk" = "web_sales"."ws_web_page_sk"
  GROUP BY
    "web_page"."wp_web_page_sk"
), "wr" AS (
  SELECT
    "web_page"."wp_web_page_sk" AS "wp_web_page_sk",
    SUM("web_returns"."wr_return_amt") AS "returns1",
    SUM("web_returns"."wr_net_loss") AS "profit_loss"
  FROM "web_returns" AS "web_returns"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_returns"."wr_returned_date_sk"
  JOIN "web_page_2" AS "web_page"
    ON "web_page"."wp_web_page_sk" = "web_returns"."wr_web_page_sk"
  GROUP BY
    "web_page"."wp_web_page_sk"
), "x" AS (
  SELECT
    'store channel' AS "channel",
    "ss"."s_store_sk" AS "id",
    "ss"."sales" AS "sales",
    COALESCE("sr"."returns1", 0) AS "returns1",
    "ss"."profit" - COALESCE("sr"."profit_loss", 0) AS "profit"
  FROM "ss" AS "ss"
  LEFT JOIN "sr" AS "sr"
    ON "sr"."s_store_sk" = "ss"."s_store_sk"
  UNION ALL
  SELECT
    'catalog channel' AS "channel",
    "cs"."cs_call_center_sk" AS "id",
    "cs"."sales" AS "sales",
    "cr"."returns1" AS "returns1",
    "cs"."profit" - "cr"."profit_loss" AS "profit"
  FROM "cs" AS "cs"
  CROSS JOIN "cr" AS "cr"
  UNION ALL
  SELECT
    'web channel' AS "channel",
    "ws"."wp_web_page_sk" AS "id",
    "ws"."sales" AS "sales",
    COALESCE("wr"."returns1", 0) AS "returns1",
    "ws"."profit" - COALESCE("wr"."profit_loss", 0) AS "profit"
  FROM "ws" AS "ws"
  LEFT JOIN "wr" AS "wr"
    ON "wr"."wp_web_page_sk" = "ws"."wp_web_page_sk"
)
SELECT
  "x"."channel" AS "channel",
  "x"."id" AS "id",
  SUM("x"."sales") AS "sales",
  SUM("x"."returns1") AS "returns1",
  SUM("x"."profit") AS "profit"
FROM "x" AS "x"
GROUP BY
  ROLLUP (
    "x"."channel",
    "x"."id"
  )
ORDER BY
  "channel",
  "id"
LIMIT 100;
