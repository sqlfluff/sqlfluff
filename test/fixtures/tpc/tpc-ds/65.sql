--------------------------------------
-- TPC-DS 65
--------------------------------------
SELECT s_store_name,
               i_item_desc,
               sc.revenue,
               i_current_price,
               i_wholesale_cost,
               i_brand
FROM   store,
       item,
       (SELECT ss_store_sk,
               Avg(revenue) AS ave
        FROM   (SELECT ss_store_sk,
                       ss_item_sk,
                       Sum(ss_sales_price) AS revenue
                FROM   store_sales,
                       date_dim
                WHERE  ss_sold_date_sk = d_date_sk
                       AND d_month_seq BETWEEN 1199 AND 1199 + 11
                GROUP  BY ss_store_sk,
                          ss_item_sk) sa
        GROUP  BY ss_store_sk) sb,
       (SELECT ss_store_sk,
               ss_item_sk,
               Sum(ss_sales_price) AS revenue
        FROM   store_sales,
               date_dim
        WHERE  ss_sold_date_sk = d_date_sk
               AND d_month_seq BETWEEN 1199 AND 1199 + 11
        GROUP  BY ss_store_sk,
                  ss_item_sk) sc
WHERE  sb.ss_store_sk = sc.ss_store_sk
       AND sc.revenue <= 0.1 * sb.ave
       AND s_store_sk = sc.ss_store_sk
       AND i_item_sk = sc.ss_item_sk
ORDER  BY s_store_name,
          i_item_desc
LIMIT 100;
WITH "store_sales_2" AS (
  SELECT
    "store_sales"."ss_sold_date_sk" AS "ss_sold_date_sk",
    "store_sales"."ss_item_sk" AS "ss_item_sk",
    "store_sales"."ss_store_sk" AS "ss_store_sk",
    "store_sales"."ss_sales_price" AS "ss_sales_price"
  FROM "store_sales" AS "store_sales"
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_month_seq" AS "d_month_seq"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_month_seq" <= 1210 AND "date_dim"."d_month_seq" >= 1199
), "sc" AS (
  SELECT
    "store_sales"."ss_store_sk" AS "ss_store_sk",
    "store_sales"."ss_item_sk" AS "ss_item_sk",
    SUM("store_sales"."ss_sales_price") AS "revenue"
  FROM "store_sales_2" AS "store_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  GROUP BY
    "store_sales"."ss_store_sk",
    "store_sales"."ss_item_sk"
), "sa" AS (
  SELECT
    "store_sales"."ss_store_sk" AS "ss_store_sk",
    SUM("store_sales"."ss_sales_price") AS "revenue"
  FROM "store_sales_2" AS "store_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  GROUP BY
    "store_sales"."ss_store_sk",
    "store_sales"."ss_item_sk"
), "sb" AS (
  SELECT
    "sa"."ss_store_sk" AS "ss_store_sk",
    AVG("sa"."revenue") AS "ave"
  FROM "sa" AS "sa"
  GROUP BY
    "sa"."ss_store_sk"
)
SELECT
  "store"."s_store_name" AS "s_store_name",
  "item"."i_item_desc" AS "i_item_desc",
  "sc"."revenue" AS "revenue",
  "item"."i_current_price" AS "i_current_price",
  "item"."i_wholesale_cost" AS "i_wholesale_cost",
  "item"."i_brand" AS "i_brand"
FROM "store" AS "store"
JOIN "sc" AS "sc"
  ON "sc"."ss_store_sk" = "store"."s_store_sk"
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "sc"."ss_item_sk"
JOIN "sb" AS "sb"
  ON "sb"."ss_store_sk" = "sc"."ss_store_sk" AND "sc"."revenue" <= 0.1 * "sb"."ave"
ORDER BY
  "s_store_name",
  "i_item_desc"
LIMIT 100;
