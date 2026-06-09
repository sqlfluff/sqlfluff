--------------------------------------
-- TPC-DS 14
--------------------------------------
WITH cross_items
     AS (SELECT i_item_sk ss_item_sk
         FROM   item,
                (SELECT iss.i_brand_id    brand_id,
                        iss.i_class_id    class_id,
                        iss.i_category_id category_id
                 FROM   store_sales,
                        item iss,
                        date_dim d1
                 WHERE  ss_item_sk = iss.i_item_sk
                        AND ss_sold_date_sk = d1.d_date_sk
                        AND d1.d_year BETWEEN 1999 AND 1999 + 2
                 INTERSECT
                 SELECT ics.i_brand_id,
                        ics.i_class_id,
                        ics.i_category_id
                 FROM   catalog_sales,
                        item ics,
                        date_dim d2
                 WHERE  cs_item_sk = ics.i_item_sk
                        AND cs_sold_date_sk = d2.d_date_sk
                        AND d2.d_year BETWEEN 1999 AND 1999 + 2
                 INTERSECT
                 SELECT iws.i_brand_id,
                        iws.i_class_id,
                        iws.i_category_id
                 FROM   web_sales,
                        item iws,
                        date_dim d3
                 WHERE  ws_item_sk = iws.i_item_sk
                        AND ws_sold_date_sk = d3.d_date_sk
                        AND d3.d_year BETWEEN 1999 AND 1999 + 2)
         WHERE  i_brand_id = brand_id
                AND i_class_id = class_id
                AND i_category_id = category_id),
     avg_sales
     AS (SELECT Avg(quantity * list_price) average_sales
         FROM   (SELECT ss_quantity   quantity,
                        ss_list_price list_price
                 FROM   store_sales,
                        date_dim
                 WHERE  ss_sold_date_sk = d_date_sk
                        AND d_year BETWEEN 1999 AND 1999 + 2
                 UNION ALL
                 SELECT cs_quantity   quantity,
                        cs_list_price list_price
                 FROM   catalog_sales,
                        date_dim
                 WHERE  cs_sold_date_sk = d_date_sk
                        AND d_year BETWEEN 1999 AND 1999 + 2
                 UNION ALL
                 SELECT ws_quantity   quantity,
                        ws_list_price list_price
                 FROM   web_sales,
                        date_dim
                 WHERE  ws_sold_date_sk = d_date_sk
                        AND d_year BETWEEN 1999 AND 1999 + 2) x)
SELECT channel,
               i_brand_id,
               i_class_id,
               i_category_id,
               Sum(sales),
               Sum(number_sales)
FROM  (SELECT 'store'                          channel,
              i_brand_id,
              i_class_id,
              i_category_id,
              Sum(ss_quantity * ss_list_price) sales,
              Count(*)                         number_sales
       FROM   store_sales,
              item,
              date_dim
       WHERE  ss_item_sk IN (SELECT ss_item_sk
                             FROM   cross_items)
              AND ss_item_sk = i_item_sk
              AND ss_sold_date_sk = d_date_sk
              AND d_year = 1999 + 2
              AND d_moy = 11
       GROUP  BY i_brand_id,
                 i_class_id,
                 i_category_id
       HAVING Sum(ss_quantity * ss_list_price) > (SELECT average_sales
                                                  FROM   avg_sales)
       UNION ALL
       SELECT 'catalog'                        channel,
              i_brand_id,
              i_class_id,
              i_category_id,
              Sum(cs_quantity * cs_list_price) sales,
              Count(*)                         number_sales
       FROM   catalog_sales,
              item,
              date_dim
       WHERE  cs_item_sk IN (SELECT ss_item_sk
                             FROM   cross_items)
              AND cs_item_sk = i_item_sk
              AND cs_sold_date_sk = d_date_sk
              AND d_year = 1999 + 2
              AND d_moy = 11
       GROUP  BY i_brand_id,
                 i_class_id,
                 i_category_id
       HAVING Sum(cs_quantity * cs_list_price) > (SELECT average_sales
                                                  FROM   avg_sales)
       UNION ALL
       SELECT 'web'                            channel,
              i_brand_id,
              i_class_id,
              i_category_id,
              Sum(ws_quantity * ws_list_price) sales,
              Count(*)                         number_sales
       FROM   web_sales,
              item,
              date_dim
       WHERE  ws_item_sk IN (SELECT ss_item_sk
                             FROM   cross_items)
              AND ws_item_sk = i_item_sk
              AND ws_sold_date_sk = d_date_sk
              AND d_year = 1999 + 2
              AND d_moy = 11
       GROUP  BY i_brand_id,
                 i_class_id,
                 i_category_id
       HAVING Sum(ws_quantity * ws_list_price) > (SELECT average_sales
                                                  FROM   avg_sales)) y
GROUP  BY rollup ( channel, i_brand_id, i_class_id, i_category_id )
ORDER  BY channel,
          i_brand_id,
          i_class_id,
          i_category_id
LIMIT 100;
WITH "item_2" AS (
  SELECT
    "item"."i_item_sk" AS "i_item_sk",
    "item"."i_brand_id" AS "i_brand_id",
    "item"."i_class_id" AS "i_class_id",
    "item"."i_category_id" AS "i_category_id"
  FROM "item" AS "item"
), "_0" AS (
  SELECT
    "iss"."i_brand_id" AS "brand_id",
    "iss"."i_class_id" AS "class_id",
    "iss"."i_category_id" AS "category_id"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim" AS "d1"
    ON "d1"."d_date_sk" = "store_sales"."ss_sold_date_sk"
    AND "d1"."d_year" <= 2001
    AND "d1"."d_year" >= 1999
  JOIN "item" AS "iss"
    ON "iss"."i_item_sk" = "store_sales"."ss_item_sk"
  INTERSECT
  SELECT
    "ics"."i_brand_id" AS "i_brand_id",
    "ics"."i_class_id" AS "i_class_id",
    "ics"."i_category_id" AS "i_category_id"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "date_dim" AS "d2"
    ON "catalog_sales"."cs_sold_date_sk" = "d2"."d_date_sk"
    AND "d2"."d_year" <= 2001
    AND "d2"."d_year" >= 1999
  JOIN "item" AS "ics"
    ON "catalog_sales"."cs_item_sk" = "ics"."i_item_sk"
  INTERSECT
  SELECT
    "iws"."i_brand_id" AS "i_brand_id",
    "iws"."i_class_id" AS "i_class_id",
    "iws"."i_category_id" AS "i_category_id"
  FROM "web_sales" AS "web_sales"
  JOIN "date_dim" AS "d3"
    ON "d3"."d_date_sk" = "web_sales"."ws_sold_date_sk"
    AND "d3"."d_year" <= 2001
    AND "d3"."d_year" >= 1999
  JOIN "item" AS "iws"
    ON "iws"."i_item_sk" = "web_sales"."ws_item_sk"
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_year" <= 2001 AND "date_dim"."d_year" >= 1999
), "x" AS (
  SELECT
    "store_sales"."ss_quantity" AS "quantity",
    "store_sales"."ss_list_price" AS "list_price"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  UNION ALL
  SELECT
    "catalog_sales"."cs_quantity" AS "quantity",
    "catalog_sales"."cs_list_price" AS "list_price"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  UNION ALL
  SELECT
    "web_sales"."ws_quantity" AS "quantity",
    "web_sales"."ws_list_price" AS "list_price"
  FROM "web_sales" AS "web_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
), "avg_sales" AS (
  SELECT
    AVG("x"."quantity" * "x"."list_price") AS "average_sales"
  FROM "x" AS "x"
), "date_dim_3" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year",
    "date_dim"."d_moy" AS "d_moy"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_moy" = 11 AND "date_dim"."d_year" = 2001
), "_u_0" AS (
  SELECT
    "item"."i_item_sk" AS "ss_item_sk"
  FROM "item_2" AS "item"
  JOIN "_0" AS "_0"
    ON "_0"."brand_id" = "item"."i_brand_id"
    AND "_0"."category_id" = "item"."i_category_id"
    AND "_0"."class_id" = "item"."i_class_id"
  GROUP BY
    "item"."i_item_sk"
), "_u_1" AS (
  SELECT
    "avg_sales"."average_sales" AS "average_sales"
  FROM "avg_sales" AS "avg_sales"
), "y" AS (
  SELECT
    'store' AS "channel",
    "item"."i_brand_id" AS "i_brand_id",
    "item"."i_class_id" AS "i_class_id",
    "item"."i_category_id" AS "i_category_id",
    SUM("store_sales"."ss_quantity" * "store_sales"."ss_list_price") AS "sales",
    COUNT(*) AS "number_sales"
  FROM "store_sales" AS "store_sales"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "date_dim_3" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  LEFT JOIN "_u_0" AS "_u_0"
    ON "_u_0"."ss_item_sk" = "store_sales"."ss_item_sk"
  CROSS JOIN "_u_1" AS "_u_1"
  WHERE
    NOT "_u_0"."ss_item_sk" IS NULL
  GROUP BY
    "item"."i_brand_id",
    "item"."i_class_id",
    "item"."i_category_id"
  HAVING
    MAX("_u_1"."average_sales") < SUM("store_sales"."ss_quantity" * "store_sales"."ss_list_price")
  UNION ALL
  SELECT
    'catalog' AS "channel",
    "item"."i_brand_id" AS "i_brand_id",
    "item"."i_class_id" AS "i_class_id",
    "item"."i_category_id" AS "i_category_id",
    SUM("catalog_sales"."cs_quantity" * "catalog_sales"."cs_list_price") AS "sales",
    COUNT(*) AS "number_sales"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "item_2" AS "item"
    ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
  JOIN "date_dim_3" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  LEFT JOIN "_u_0" AS "_u_2"
    ON "_u_2"."ss_item_sk" = "catalog_sales"."cs_item_sk"
  CROSS JOIN "_u_1" AS "_u_3"
  WHERE
    NOT "_u_2"."ss_item_sk" IS NULL
  GROUP BY
    "item"."i_brand_id",
    "item"."i_class_id",
    "item"."i_category_id"
  HAVING
    MAX("_u_3"."average_sales") < SUM("catalog_sales"."cs_quantity" * "catalog_sales"."cs_list_price")
  UNION ALL
  SELECT
    'web' AS "channel",
    "item"."i_brand_id" AS "i_brand_id",
    "item"."i_class_id" AS "i_class_id",
    "item"."i_category_id" AS "i_category_id",
    SUM("web_sales"."ws_quantity" * "web_sales"."ws_list_price") AS "sales",
    COUNT(*) AS "number_sales"
  FROM "web_sales" AS "web_sales"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "web_sales"."ws_item_sk"
  JOIN "date_dim_3" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  LEFT JOIN "_u_0" AS "_u_4"
    ON "_u_4"."ss_item_sk" = "web_sales"."ws_item_sk"
  CROSS JOIN "_u_1" AS "_u_5"
  WHERE
    NOT "_u_4"."ss_item_sk" IS NULL
  GROUP BY
    "item"."i_brand_id",
    "item"."i_class_id",
    "item"."i_category_id"
  HAVING
    MAX("_u_5"."average_sales") < SUM("web_sales"."ws_quantity" * "web_sales"."ws_list_price")
)
SELECT
  "y"."channel" AS "channel",
  "y"."i_brand_id" AS "i_brand_id",
  "y"."i_class_id" AS "i_class_id",
  "y"."i_category_id" AS "i_category_id",
  SUM("y"."sales") AS "_col_4",
  SUM("y"."number_sales") AS "_col_5"
FROM "y" AS "y"
GROUP BY
  ROLLUP (
    "y"."channel",
    "y"."i_brand_id",
    "y"."i_class_id",
    "y"."i_category_id"
  )
ORDER BY
  "channel",
  "i_brand_id",
  "i_class_id",
  "i_category_id"
LIMIT 100;
