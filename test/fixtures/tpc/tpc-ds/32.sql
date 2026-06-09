--------------------------------------
-- TPC-DS 32
--------------------------------------
SELECT
       Sum(cs_ext_discount_amt) AS "excess discount amount"
FROM   catalog_sales ,
       item ,
       date_dim
WHERE  i_manufact_id = 610
AND    i_item_sk = cs_item_sk
AND    d_date BETWEEN '2001-03-04' AND    (
              Cast('2001-03-04' AS DATE) + INTERVAL '90' day)
AND    d_date_sk = cs_sold_date_sk
AND    cs_ext_discount_amt >
       (
              SELECT 1.3 * avg(cs_ext_discount_amt)
              FROM   catalog_sales ,
                     date_dim
              WHERE  cs_item_sk = i_item_sk
              AND    d_date BETWEEN '2001-03-04' AND    (
                            cast('2001-03-04' AS date) + INTERVAL '90' day)
              AND    d_date_sk = cs_sold_date_sk )
LIMIT 100;
WITH "catalog_sales_2" AS (
  SELECT
    "catalog_sales"."cs_sold_date_sk" AS "cs_sold_date_sk",
    "catalog_sales"."cs_item_sk" AS "cs_item_sk",
    "catalog_sales"."cs_ext_discount_amt" AS "cs_ext_discount_amt"
  FROM "catalog_sales" AS "catalog_sales"
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_date" AS "d_date"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_date" >= '2001-03-04'
    AND CAST("date_dim"."d_date" AS DATE) <= CAST('2001-06-02' AS DATE)
), "_u_0" AS (
  SELECT
    1.3 * AVG("catalog_sales"."cs_ext_discount_amt") AS "_col_0",
    "catalog_sales"."cs_item_sk" AS "_u_1"
  FROM "catalog_sales_2" AS "catalog_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  GROUP BY
    "catalog_sales"."cs_item_sk"
)
SELECT
  SUM("catalog_sales"."cs_ext_discount_amt") AS "excess discount amount"
FROM "catalog_sales_2" AS "catalog_sales"
JOIN "item" AS "item"
  ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
  AND "item"."i_manufact_id" = 610
JOIN "date_dim_2" AS "date_dim"
  ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "item"."i_item_sk"
WHERE
  "_u_0"."_col_0" < "catalog_sales"."cs_ext_discount_amt"
LIMIT 100;
