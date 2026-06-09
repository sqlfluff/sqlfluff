--------------------------------------
-- TPC-DS 51
--------------------------------------
WITH web_v1 AS
(
         SELECT   ws_item_sk item_sk,
                  d_date,
                  sum(Sum(ws_sales_price)) OVER (partition BY ws_item_sk ORDER BY d_date rows BETWEEN UNBOUNDED PRECEDING AND      CURRENT row) cume_sales
         FROM     web_sales ,
                  date_dim
         WHERE    ws_sold_date_sk=d_date_sk
         AND      d_month_seq BETWEEN 1192 AND      1192+11
         AND      ws_item_sk IS NOT NULL
         GROUP BY ws_item_sk,
                  d_date), store_v1 AS
(
         SELECT   ss_item_sk item_sk,
                  d_date,
                  sum(sum(ss_sales_price)) OVER (partition BY ss_item_sk ORDER BY d_date rows BETWEEN UNBOUNDED PRECEDING AND      CURRENT row) cume_sales
         FROM     store_sales ,
                  date_dim
         WHERE    ss_sold_date_sk=d_date_sk
         AND      d_month_seq BETWEEN 1192 AND      1192+11
         AND      ss_item_sk IS NOT NULL
         GROUP BY ss_item_sk,
                  d_date)
SELECT
         *
FROM     (
                  SELECT   item_sk ,
                           d_date ,
                           web_sales ,
                           store_sales ,
                           max(web_sales) OVER (partition BY item_sk ORDER BY d_date rows BETWEEN UNBOUNDED PRECEDING AND      CURRENT row)   web_cumulative ,
                           max(store_sales) OVER (partition BY item_sk ORDER BY d_date rows BETWEEN UNBOUNDED PRECEDING AND      CURRENT row) store_cumulative
                  FROM     (
                                           SELECT
                                                           CASE
                                                                           WHEN web.item_sk IS NOT NULL THEN web.item_sk
                                                                           ELSE store.item_sk
                                                           END item_sk ,
                                                           CASE
                                                                           WHEN web.d_date IS NOT NULL THEN web.d_date
                                                                           ELSE store.d_date
                                                           END              d_date ,
                                                           web.cume_sales   web_sales ,
                                                           store.cume_sales store_sales
                                           FROM            web_v1 web
                                           FULL OUTER JOIN store_v1 store
                                           ON              (
                                                                           web.item_sk = store.item_sk
                                                           AND             web.d_date = store.d_date) )x )y
WHERE    web_cumulative > store_cumulative
ORDER BY item_sk ,
         d_date
LIMIT 100;
WITH "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_date" AS "d_date",
    "date_dim"."d_month_seq" AS "d_month_seq"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_month_seq" <= 1203 AND "date_dim"."d_month_seq" >= 1192
), "web_v1" AS (
  SELECT
    "web_sales"."ws_item_sk" AS "item_sk",
    "date_dim"."d_date" AS "d_date",
    SUM(SUM("web_sales"."ws_sales_price")) OVER (
      PARTITION BY "web_sales"."ws_item_sk"
      ORDER BY "date_dim"."d_date"
      rows BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS "cume_sales"
  FROM "web_sales" AS "web_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  WHERE
    NOT "web_sales"."ws_item_sk" IS NULL
  GROUP BY
    "web_sales"."ws_item_sk",
    "date_dim"."d_date"
), "store_v1" AS (
  SELECT
    "store_sales"."ss_item_sk" AS "item_sk",
    "date_dim"."d_date" AS "d_date",
    SUM(SUM("store_sales"."ss_sales_price")) OVER (
      PARTITION BY "store_sales"."ss_item_sk"
      ORDER BY "date_dim"."d_date"
      rows BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS "cume_sales"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  WHERE
    NOT "store_sales"."ss_item_sk" IS NULL
  GROUP BY
    "store_sales"."ss_item_sk",
    "date_dim"."d_date"
), "y" AS (
  SELECT
    CASE
      WHEN NOT "web"."item_sk" IS NULL
      THEN "web"."item_sk"
      ELSE "store"."item_sk"
    END AS "item_sk",
    CASE WHEN NOT "web"."d_date" IS NULL THEN "web"."d_date" ELSE "store"."d_date" END AS "d_date",
    "web"."cume_sales" AS "web_sales",
    "store"."cume_sales" AS "store_sales",
    MAX("web"."cume_sales") OVER (
      PARTITION BY CASE
        WHEN NOT "web"."item_sk" IS NULL
        THEN "web"."item_sk"
        ELSE "store"."item_sk"
      END
      ORDER BY CASE WHEN NOT "web"."d_date" IS NULL THEN "web"."d_date" ELSE "store"."d_date" END
      rows BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS "web_cumulative",
    MAX("store"."cume_sales") OVER (
      PARTITION BY CASE
        WHEN NOT "web"."item_sk" IS NULL
        THEN "web"."item_sk"
        ELSE "store"."item_sk"
      END
      ORDER BY CASE WHEN NOT "web"."d_date" IS NULL THEN "web"."d_date" ELSE "store"."d_date" END
      rows BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS "store_cumulative"
  FROM "web_v1" AS "web"
  FULL JOIN "store_v1" AS "store"
    ON "store"."d_date" = "web"."d_date" AND "store"."item_sk" = "web"."item_sk"
)
SELECT
  "y"."item_sk" AS "item_sk",
  "y"."d_date" AS "d_date",
  "y"."web_sales" AS "web_sales",
  "y"."store_sales" AS "store_sales",
  "y"."web_cumulative" AS "web_cumulative",
  "y"."store_cumulative" AS "store_cumulative"
FROM "y" AS "y"
WHERE
  "y"."store_cumulative" < "y"."web_cumulative"
ORDER BY
  "y"."item_sk",
  "y"."d_date"
LIMIT 100;
