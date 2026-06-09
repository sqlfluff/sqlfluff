--------------------------------------
-- TPC-DS 60
--------------------------------------
WITH ss
     AS (SELECT i_item_id,
                Sum(ss_ext_sales_price) total_sales
         FROM   store_sales,
                date_dim,
                customer_address,
                item
         WHERE  i_item_id IN (SELECT i_item_id
                              FROM   item
                              WHERE  i_category IN ( 'Jewelry' ))
                AND ss_item_sk = i_item_sk
                AND ss_sold_date_sk = d_date_sk
                AND d_year = 1999
                AND d_moy = 8
                AND ss_addr_sk = ca_address_sk
                AND ca_gmt_offset = -6
         GROUP  BY i_item_id),
     cs
     AS (SELECT i_item_id,
                Sum(cs_ext_sales_price) total_sales
         FROM   catalog_sales,
                date_dim,
                customer_address,
                item
         WHERE  i_item_id IN (SELECT i_item_id
                              FROM   item
                              WHERE  i_category IN ( 'Jewelry' ))
                AND cs_item_sk = i_item_sk
                AND cs_sold_date_sk = d_date_sk
                AND d_year = 1999
                AND d_moy = 8
                AND cs_bill_addr_sk = ca_address_sk
                AND ca_gmt_offset = -6
         GROUP  BY i_item_id),
     ws
     AS (SELECT i_item_id,
                Sum(ws_ext_sales_price) total_sales
         FROM   web_sales,
                date_dim,
                customer_address,
                item
         WHERE  i_item_id IN (SELECT i_item_id
                              FROM   item
                              WHERE  i_category IN ( 'Jewelry' ))
                AND ws_item_sk = i_item_sk
                AND ws_sold_date_sk = d_date_sk
                AND d_year = 1999
                AND d_moy = 8
                AND ws_bill_addr_sk = ca_address_sk
                AND ca_gmt_offset = -6
         GROUP  BY i_item_id)
SELECT i_item_id,
               Sum(total_sales) total_sales
FROM   (SELECT *
        FROM   ss
        UNION ALL
        SELECT *
        FROM   cs
        UNION ALL
        SELECT *
        FROM   ws) tmp1
GROUP  BY i_item_id
ORDER  BY i_item_id,
          total_sales
LIMIT 100;
WITH "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year",
    "date_dim"."d_moy" AS "d_moy"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_moy" = 8 AND "date_dim"."d_year" = 1999
), "customer_address_2" AS (
  SELECT
    "customer_address"."ca_address_sk" AS "ca_address_sk",
    "customer_address"."ca_gmt_offset" AS "ca_gmt_offset"
  FROM "customer_address" AS "customer_address"
  WHERE
    "customer_address"."ca_gmt_offset" = -6
), "item_2" AS (
  SELECT
    "item"."i_item_sk" AS "i_item_sk",
    "item"."i_item_id" AS "i_item_id"
  FROM "item" AS "item"
), "_u_0" AS (
  SELECT
    "item"."i_item_id" AS "i_item_id"
  FROM "item" AS "item"
  WHERE
    "item"."i_category" IN ('Jewelry')
  GROUP BY
    "item"."i_item_id"
), "ss" AS (
  SELECT
    "item"."i_item_id" AS "i_item_id",
    SUM("store_sales"."ss_ext_sales_price") AS "total_sales"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  JOIN "customer_address_2" AS "customer_address"
    ON "customer_address"."ca_address_sk" = "store_sales"."ss_addr_sk"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  LEFT JOIN "_u_0" AS "_u_0"
    ON "_u_0"."i_item_id" = "item"."i_item_id"
  WHERE
    NOT "_u_0"."i_item_id" IS NULL
  GROUP BY
    "item"."i_item_id"
), "cs" AS (
  SELECT
    "item"."i_item_id" AS "i_item_id",
    SUM("catalog_sales"."cs_ext_sales_price") AS "total_sales"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  JOIN "customer_address_2" AS "customer_address"
    ON "catalog_sales"."cs_bill_addr_sk" = "customer_address"."ca_address_sk"
  JOIN "item_2" AS "item"
    ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
  LEFT JOIN "_u_0" AS "_u_1"
    ON "_u_1"."i_item_id" = "item"."i_item_id"
  WHERE
    NOT "_u_1"."i_item_id" IS NULL
  GROUP BY
    "item"."i_item_id"
), "ws" AS (
  SELECT
    "item"."i_item_id" AS "i_item_id",
    SUM("web_sales"."ws_ext_sales_price") AS "total_sales"
  FROM "web_sales" AS "web_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  JOIN "customer_address_2" AS "customer_address"
    ON "customer_address"."ca_address_sk" = "web_sales"."ws_bill_addr_sk"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "web_sales"."ws_item_sk"
  LEFT JOIN "_u_0" AS "_u_2"
    ON "_u_2"."i_item_id" = "item"."i_item_id"
  WHERE
    NOT "_u_2"."i_item_id" IS NULL
  GROUP BY
    "item"."i_item_id"
), "tmp1" AS (
  SELECT
    "ss"."i_item_id" AS "i_item_id",
    "ss"."total_sales" AS "total_sales"
  FROM "ss" AS "ss"
  UNION ALL
  SELECT
    "cs"."i_item_id" AS "i_item_id",
    "cs"."total_sales" AS "total_sales"
  FROM "cs" AS "cs"
  UNION ALL
  SELECT
    "ws"."i_item_id" AS "i_item_id",
    "ws"."total_sales" AS "total_sales"
  FROM "ws" AS "ws"
)
SELECT
  "tmp1"."i_item_id" AS "i_item_id",
  SUM("tmp1"."total_sales") AS "total_sales"
FROM "tmp1" AS "tmp1"
GROUP BY
  "tmp1"."i_item_id"
ORDER BY
  "i_item_id",
  "total_sales"
LIMIT 100;
