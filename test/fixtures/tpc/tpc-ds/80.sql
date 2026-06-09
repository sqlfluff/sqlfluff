--------------------------------------
-- TPC-DS 80
--------------------------------------
WITH ssr AS
(
                SELECT          s_store_id                                    AS store_id,
                                Sum(ss_ext_sales_price)                       AS sales,
                                Sum(COALESCE(sr_return_amt, 0))               AS returns1,
                                Sum(ss_net_profit - COALESCE(sr_net_loss, 0)) AS profit
                FROM            store_sales
                LEFT OUTER JOIN store_returns
                ON              (
                                                ss_item_sk = sr_item_sk
                                AND             ss_ticket_number = sr_ticket_number),
                                date_dim,
                                store,
                                item,
                                promotion
                WHERE           ss_sold_date_sk = d_date_sk
                AND             d_date BETWEEN Cast('2000-08-26' AS DATE) AND             (
                                                Cast('2000-08-26' AS DATE) + INTERVAL '30' day)
                AND             ss_store_sk = s_store_sk
                AND             ss_item_sk = i_item_sk
                AND             i_current_price > 50
                AND             ss_promo_sk = p_promo_sk
                AND             p_channel_tv = 'N'
                GROUP BY        s_store_id) , csr AS
(
                SELECT          cp_catalog_page_id                            AS catalog_page_id,
                                sum(cs_ext_sales_price)                       AS sales,
                                sum(COALESCE(cr_return_amount, 0))            AS returns1,
                                sum(cs_net_profit - COALESCE(cr_net_loss, 0)) AS profit
                FROM            catalog_sales
                LEFT OUTER JOIN catalog_returns
                ON              (
                                                cs_item_sk = cr_item_sk
                                AND             cs_order_number = cr_order_number),
                                date_dim,
                                catalog_page,
                                item,
                                promotion
                WHERE           cs_sold_date_sk = d_date_sk
                AND             d_date BETWEEN cast('2000-08-26' AS date) AND             (
                                                cast('2000-08-26' AS date) + INTERVAL '30' day)
                AND             cs_catalog_page_sk = cp_catalog_page_sk
                AND             cs_item_sk = i_item_sk
                AND             i_current_price > 50
                AND             cs_promo_sk = p_promo_sk
                AND             p_channel_tv = 'N'
                GROUP BY        cp_catalog_page_id) , wsr AS
(
                SELECT          web_site_id,
                                sum(ws_ext_sales_price)                       AS sales,
                                sum(COALESCE(wr_return_amt, 0))               AS returns1,
                                sum(ws_net_profit - COALESCE(wr_net_loss, 0)) AS profit
                FROM            web_sales
                LEFT OUTER JOIN web_returns
                ON              (
                                                ws_item_sk = wr_item_sk
                                AND             ws_order_number = wr_order_number),
                                date_dim,
                                web_site,
                                item,
                                promotion
                WHERE           ws_sold_date_sk = d_date_sk
                AND             d_date BETWEEN cast('2000-08-26' AS date) AND             (
                                                cast('2000-08-26' AS date) + INTERVAL '30' day)
                AND             ws_web_site_sk = web_site_sk
                AND             ws_item_sk = i_item_sk
                AND             i_current_price > 50
                AND             ws_promo_sk = p_promo_sk
                AND             p_channel_tv = 'N'
                GROUP BY        web_site_id)
SELECT
         channel ,
         id ,
         sum(sales)   AS sales ,
         sum(returns1) AS returns1 ,
         sum(profit)  AS profit
FROM     (
                SELECT 'store channel' AS channel ,
                       'store'
                              || store_id AS id ,
                       sales ,
                       returns1 ,
                       profit
                FROM   ssr
                UNION ALL
                SELECT 'catalog channel' AS channel ,
                       'catalog_page'
                              || catalog_page_id AS id ,
                       sales ,
                       returns1 ,
                       profit
                FROM   csr
                UNION ALL
                SELECT 'web channel' AS channel ,
                       'web_site'
                              || web_site_id AS id ,
                       sales ,
                       returns1 ,
                       profit
                FROM   wsr ) x
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
    CAST("date_dim"."d_date" AS DATE) <= CAST('2000-09-25' AS DATE)
    AND CAST("date_dim"."d_date" AS DATE) >= CAST('2000-08-26' AS DATE)
), "item_2" AS (
  SELECT
    "item"."i_item_sk" AS "i_item_sk",
    "item"."i_current_price" AS "i_current_price"
  FROM "item" AS "item"
  WHERE
    "item"."i_current_price" > 50
), "promotion_2" AS (
  SELECT
    "promotion"."p_promo_sk" AS "p_promo_sk",
    "promotion"."p_channel_tv" AS "p_channel_tv"
  FROM "promotion" AS "promotion"
  WHERE
    "promotion"."p_channel_tv" = 'N'
), "ssr" AS (
  SELECT
    "store"."s_store_id" AS "store_id",
    SUM("store_sales"."ss_ext_sales_price") AS "sales",
    SUM(COALESCE("store_returns"."sr_return_amt", 0)) AS "returns1",
    SUM("store_sales"."ss_net_profit" - COALESCE("store_returns"."sr_net_loss", 0)) AS "profit"
  FROM "store_sales" AS "store_sales"
  LEFT JOIN "store_returns" AS "store_returns"
    ON "store_returns"."sr_item_sk" = "store_sales"."ss_item_sk"
    AND "store_returns"."sr_ticket_number" = "store_sales"."ss_ticket_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  JOIN "store" AS "store"
    ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "promotion_2" AS "promotion"
    ON "promotion"."p_promo_sk" = "store_sales"."ss_promo_sk"
  GROUP BY
    "store"."s_store_id"
), "csr" AS (
  SELECT
    "catalog_page"."cp_catalog_page_id" AS "catalog_page_id",
    SUM("catalog_sales"."cs_ext_sales_price") AS "sales",
    SUM(COALESCE("catalog_returns"."cr_return_amount", 0)) AS "returns1",
    SUM("catalog_sales"."cs_net_profit" - COALESCE("catalog_returns"."cr_net_loss", 0)) AS "profit"
  FROM "catalog_sales" AS "catalog_sales"
  LEFT JOIN "catalog_returns" AS "catalog_returns"
    ON "catalog_returns"."cr_item_sk" = "catalog_sales"."cs_item_sk"
    AND "catalog_returns"."cr_order_number" = "catalog_sales"."cs_order_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  JOIN "catalog_page" AS "catalog_page"
    ON "catalog_page"."cp_catalog_page_sk" = "catalog_sales"."cs_catalog_page_sk"
  JOIN "item_2" AS "item"
    ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
  JOIN "promotion_2" AS "promotion"
    ON "catalog_sales"."cs_promo_sk" = "promotion"."p_promo_sk"
  GROUP BY
    "catalog_page"."cp_catalog_page_id"
), "wsr" AS (
  SELECT
    "web_site"."web_site_id" AS "web_site_id",
    SUM("web_sales"."ws_ext_sales_price") AS "sales",
    SUM(COALESCE("web_returns"."wr_return_amt", 0)) AS "returns1",
    SUM("web_sales"."ws_net_profit" - COALESCE("web_returns"."wr_net_loss", 0)) AS "profit"
  FROM "web_sales" AS "web_sales"
  LEFT JOIN "web_returns" AS "web_returns"
    ON "web_returns"."wr_item_sk" = "web_sales"."ws_item_sk"
    AND "web_returns"."wr_order_number" = "web_sales"."ws_order_number"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  JOIN "web_site" AS "web_site"
    ON "web_sales"."ws_web_site_sk" = "web_site"."web_site_sk"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "web_sales"."ws_item_sk"
  JOIN "promotion_2" AS "promotion"
    ON "promotion"."p_promo_sk" = "web_sales"."ws_promo_sk"
  GROUP BY
    "web_site"."web_site_id"
), "x" AS (
  SELECT
    'store channel' AS "channel",
    'store' || "ssr"."store_id" AS "id",
    "ssr"."sales" AS "sales",
    "ssr"."returns1" AS "returns1",
    "ssr"."profit" AS "profit"
  FROM "ssr" AS "ssr"
  UNION ALL
  SELECT
    'catalog channel' AS "channel",
    'catalog_page' || "csr"."catalog_page_id" AS "id",
    "csr"."sales" AS "sales",
    "csr"."returns1" AS "returns1",
    "csr"."profit" AS "profit"
  FROM "csr" AS "csr"
  UNION ALL
  SELECT
    'web channel' AS "channel",
    'web_site' || "wsr"."web_site_id" AS "id",
    "wsr"."sales" AS "sales",
    "wsr"."returns1" AS "returns1",
    "wsr"."profit" AS "profit"
  FROM "wsr" AS "wsr"
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
