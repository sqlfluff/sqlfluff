--------------------------------------
-- TPC-DS 92
--------------------------------------
SELECT
         Sum(ws_ext_discount_amt) AS "Excess Discount Amount"
FROM     web_sales ,
         item ,
         date_dim
WHERE    i_manufact_id = 718
AND      i_item_sk = ws_item_sk
AND      d_date BETWEEN '2002-03-29' AND      (
                  Cast('2002-03-29' AS DATE) +  INTERVAL '90' day)
AND      d_date_sk = ws_sold_date_sk
AND      ws_ext_discount_amt >
         (
                SELECT 1.3 * avg(ws_ext_discount_amt)
                FROM   web_sales ,
                       date_dim
                WHERE  ws_item_sk = i_item_sk
                AND    d_date BETWEEN '2002-03-29' AND    (
                              cast('2002-03-29' AS date) + INTERVAL '90' day)
                AND    d_date_sk = ws_sold_date_sk )
ORDER BY sum(ws_ext_discount_amt)
LIMIT 100;
WITH "web_sales_2" AS (
  SELECT
    "web_sales"."ws_sold_date_sk" AS "ws_sold_date_sk",
    "web_sales"."ws_item_sk" AS "ws_item_sk",
    "web_sales"."ws_ext_discount_amt" AS "ws_ext_discount_amt"
  FROM "web_sales" AS "web_sales"
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_date" AS "d_date"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_date" >= '2002-03-29'
    AND CAST("date_dim"."d_date" AS DATE) <= CAST('2002-06-27' AS DATE)
), "_u_0" AS (
  SELECT
    1.3 * AVG("web_sales"."ws_ext_discount_amt") AS "_col_0",
    "web_sales"."ws_item_sk" AS "_u_1"
  FROM "web_sales_2" AS "web_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  GROUP BY
    "web_sales"."ws_item_sk"
)
SELECT
  SUM("web_sales"."ws_ext_discount_amt") AS "Excess Discount Amount"
FROM "web_sales_2" AS "web_sales"
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "web_sales"."ws_item_sk" AND "item"."i_manufact_id" = 718
JOIN "date_dim_2" AS "date_dim"
  ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "item"."i_item_sk"
WHERE
  "_u_0"."_col_0" < "web_sales"."ws_ext_discount_amt"
ORDER BY
  SUM("web_sales"."ws_ext_discount_amt")
LIMIT 100;
