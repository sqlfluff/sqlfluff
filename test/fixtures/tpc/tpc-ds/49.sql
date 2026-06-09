--------------------------------------
-- TPC-DS 49
--------------------------------------
SELECT 'web' AS channel,
               web.item,
               web.return_ratio,
               web.return_rank,
               web.currency_rank
FROM   (SELECT item,
               return_ratio,
               currency_ratio,
               Rank()
                 OVER (
                   ORDER BY return_ratio)   AS return_rank,
               Rank()
                 OVER (
                   ORDER BY currency_ratio) AS currency_rank
        FROM   (SELECT ws.ws_item_sk                                       AS
                       item,
                       ( Cast(Sum(COALESCE(wr.wr_return_quantity, 0)) AS DEC(15,
                              4)) /
                         Cast(
                         Sum(COALESCE(ws.ws_quantity, 0)) AS DEC(15, 4)) ) AS
                       return_ratio,
                       ( Cast(Sum(COALESCE(wr.wr_return_amt, 0)) AS DEC(15, 4))
                         / Cast(
                         Sum(
                         COALESCE(ws.ws_net_paid, 0)) AS DEC(15,
                         4)) )                                             AS
                       currency_ratio
                FROM   web_sales ws
                       LEFT OUTER JOIN web_returns wr
                                    ON ( ws.ws_order_number = wr.wr_order_number
                                         AND ws.ws_item_sk = wr.wr_item_sk ),
                       date_dim
                WHERE  wr.wr_return_amt > 10000
                       AND ws.ws_net_profit > 1
                       AND ws.ws_net_paid > 0
                       AND ws.ws_quantity > 0
                       AND ws_sold_date_sk = d_date_sk
                       AND d_year = 1999
                       AND d_moy = 12
                GROUP  BY ws.ws_item_sk) in_web) web
WHERE  ( web.return_rank <= 10
          OR web.currency_rank <= 10 )
UNION
SELECT 'catalog' AS channel,
       catalog.item,
       catalog.return_ratio,
       catalog.return_rank,
       catalog.currency_rank
FROM   (SELECT item,
               return_ratio,
               currency_ratio,
               Rank()
                 OVER (
                   ORDER BY return_ratio)   AS return_rank,
               Rank()
                 OVER (
                   ORDER BY currency_ratio) AS currency_rank
        FROM   (SELECT cs.cs_item_sk                                       AS
                       item,
                       ( Cast(Sum(COALESCE(cr.cr_return_quantity, 0)) AS DEC(15,
                              4)) /
                         Cast(
                         Sum(COALESCE(cs.cs_quantity, 0)) AS DEC(15, 4)) ) AS
                       return_ratio,
                       ( Cast(Sum(COALESCE(cr.cr_return_amount, 0)) AS DEC(15, 4
                              )) /
                         Cast(Sum(
                         COALESCE(cs.cs_net_paid, 0)) AS DEC(
                         15, 4)) )                                         AS
                       currency_ratio
                FROM   catalog_sales cs
                       LEFT OUTER JOIN catalog_returns cr
                                    ON ( cs.cs_order_number = cr.cr_order_number
                                         AND cs.cs_item_sk = cr.cr_item_sk ),
                       date_dim
                WHERE  cr.cr_return_amount > 10000
                       AND cs.cs_net_profit > 1
                       AND cs.cs_net_paid > 0
                       AND cs.cs_quantity > 0
                       AND cs_sold_date_sk = d_date_sk
                       AND d_year = 1999
                       AND d_moy = 12
                GROUP  BY cs.cs_item_sk) in_cat) catalog
WHERE  ( catalog.return_rank <= 10
          OR catalog.currency_rank <= 10 )
UNION
SELECT 'store' AS channel,
       store.item,
       store.return_ratio,
       store.return_rank,
       store.currency_rank
FROM   (SELECT item,
               return_ratio,
               currency_ratio,
               Rank()
                 OVER (
                   ORDER BY return_ratio)   AS return_rank,
               Rank()
                 OVER (
                   ORDER BY currency_ratio) AS currency_rank
        FROM   (SELECT sts.ss_item_sk                                       AS
                       item,
                       ( Cast(Sum(COALESCE(sr.sr_return_quantity, 0)) AS DEC(15,
                              4)) /
                         Cast(
                         Sum(COALESCE(sts.ss_quantity, 0)) AS DEC(15, 4)) ) AS
                       return_ratio,
                       ( Cast(Sum(COALESCE(sr.sr_return_amt, 0)) AS DEC(15, 4))
                         / Cast(
                         Sum(
                         COALESCE(sts.ss_net_paid, 0)) AS DEC(15, 4)) )     AS
                       currency_ratio
                FROM   store_sales sts
                       LEFT OUTER JOIN store_returns sr
                                    ON ( sts.ss_ticket_number =
                                         sr.sr_ticket_number
                                         AND sts.ss_item_sk = sr.sr_item_sk ),
                       date_dim
                WHERE  sr.sr_return_amt > 10000
                       AND sts.ss_net_profit > 1
                       AND sts.ss_net_paid > 0
                       AND sts.ss_quantity > 0
                       AND ss_sold_date_sk = d_date_sk
                       AND d_year = 1999
                       AND d_moy = 12
                GROUP  BY sts.ss_item_sk) in_store) store
WHERE  ( store.return_rank <= 10
          OR store.currency_rank <= 10 )
ORDER  BY 1,
          4,
          5
LIMIT 100;
WITH "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year",
    "date_dim"."d_moy" AS "d_moy"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_moy" = 12 AND "date_dim"."d_year" = 1999
), "in_web" AS (
  SELECT
    "ws"."ws_item_sk" AS "item",
    CAST(SUM(COALESCE("wr"."wr_return_quantity", 0)) AS DECIMAL(15, 4)) / CAST(SUM(COALESCE("ws"."ws_quantity", 0)) AS DECIMAL(15, 4)) AS "return_ratio",
    CAST(SUM(COALESCE("wr"."wr_return_amt", 0)) AS DECIMAL(15, 4)) / CAST(SUM(COALESCE("ws"."ws_net_paid", 0)) AS DECIMAL(15, 4)) AS "currency_ratio"
  FROM "web_sales" AS "ws"
  LEFT JOIN "web_returns" AS "wr"
    ON "wr"."wr_item_sk" = "ws"."ws_item_sk"
    AND "wr"."wr_order_number" = "ws"."ws_order_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "ws"."ws_sold_date_sk"
  WHERE
    "wr"."wr_return_amt" > 10000
    AND "ws"."ws_net_paid" > 0
    AND "ws"."ws_net_profit" > 1
    AND "ws"."ws_quantity" > 0
  GROUP BY
    "ws"."ws_item_sk"
), "web" AS (
  SELECT
    "in_web"."item" AS "item",
    "in_web"."return_ratio" AS "return_ratio",
    RANK() OVER (ORDER BY "in_web"."return_ratio") AS "return_rank",
    RANK() OVER (ORDER BY "in_web"."currency_ratio") AS "currency_rank"
  FROM "in_web" AS "in_web"
), "in_cat" AS (
  SELECT
    "cs"."cs_item_sk" AS "item",
    CAST(SUM(COALESCE("cr"."cr_return_quantity", 0)) AS DECIMAL(15, 4)) / CAST(SUM(COALESCE("cs"."cs_quantity", 0)) AS DECIMAL(15, 4)) AS "return_ratio",
    CAST(SUM(COALESCE("cr"."cr_return_amount", 0)) AS DECIMAL(15, 4)) / CAST(SUM(COALESCE("cs"."cs_net_paid", 0)) AS DECIMAL(15, 4)) AS "currency_ratio"
  FROM "catalog_sales" AS "cs"
  LEFT JOIN "catalog_returns" AS "cr"
    ON "cr"."cr_item_sk" = "cs"."cs_item_sk"
    AND "cr"."cr_order_number" = "cs"."cs_order_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "cs"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  WHERE
    "cr"."cr_return_amount" > 10000
    AND "cs"."cs_net_paid" > 0
    AND "cs"."cs_net_profit" > 1
    AND "cs"."cs_quantity" > 0
  GROUP BY
    "cs"."cs_item_sk"
), "catalog" AS (
  SELECT
    "in_cat"."item" AS "item",
    "in_cat"."return_ratio" AS "return_ratio",
    RANK() OVER (ORDER BY "in_cat"."return_ratio") AS "return_rank",
    RANK() OVER (ORDER BY "in_cat"."currency_ratio") AS "currency_rank"
  FROM "in_cat" AS "in_cat"
), "in_store" AS (
  SELECT
    "sts"."ss_item_sk" AS "item",
    CAST(SUM(COALESCE("sr"."sr_return_quantity", 0)) AS DECIMAL(15, 4)) / CAST(SUM(COALESCE("sts"."ss_quantity", 0)) AS DECIMAL(15, 4)) AS "return_ratio",
    CAST(SUM(COALESCE("sr"."sr_return_amt", 0)) AS DECIMAL(15, 4)) / CAST(SUM(COALESCE("sts"."ss_net_paid", 0)) AS DECIMAL(15, 4)) AS "currency_ratio"
  FROM "store_sales" AS "sts"
  LEFT JOIN "store_returns" AS "sr"
    ON "sr"."sr_item_sk" = "sts"."ss_item_sk"
    AND "sr"."sr_ticket_number" = "sts"."ss_ticket_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "sts"."ss_sold_date_sk"
  WHERE
    "sr"."sr_return_amt" > 10000
    AND "sts"."ss_net_paid" > 0
    AND "sts"."ss_net_profit" > 1
    AND "sts"."ss_quantity" > 0
  GROUP BY
    "sts"."ss_item_sk"
), "store" AS (
  SELECT
    "in_store"."item" AS "item",
    "in_store"."return_ratio" AS "return_ratio",
    RANK() OVER (ORDER BY "in_store"."return_ratio") AS "return_rank",
    RANK() OVER (ORDER BY "in_store"."currency_ratio") AS "currency_rank"
  FROM "in_store" AS "in_store"
)
SELECT
  'web' AS "channel",
  "web"."item" AS "item",
  "web"."return_ratio" AS "return_ratio",
  "web"."return_rank" AS "return_rank",
  "web"."currency_rank" AS "currency_rank"
FROM "web" AS "web"
WHERE
  "web"."currency_rank" <= 10 OR "web"."return_rank" <= 10
UNION
SELECT
  'catalog' AS "channel",
  "catalog"."item" AS "item",
  "catalog"."return_ratio" AS "return_ratio",
  "catalog"."return_rank" AS "return_rank",
  "catalog"."currency_rank" AS "currency_rank"
FROM "catalog" AS "catalog"
WHERE
  "catalog"."currency_rank" <= 10 OR "catalog"."return_rank" <= 10
UNION
SELECT
  'store' AS "channel",
  "store"."item" AS "item",
  "store"."return_ratio" AS "return_ratio",
  "store"."return_rank" AS "return_rank",
  "store"."currency_rank" AS "currency_rank"
FROM "store" AS "store"
WHERE
  "store"."currency_rank" <= 10 OR "store"."return_rank" <= 10
ORDER BY
  "channel",
  "return_rank",
  "currency_rank"
LIMIT 100;
