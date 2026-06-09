--------------------------------------
-- TPC-DS 58
--------------------------------------
WITH ss_items
     AS (SELECT i_item_id               item_id,
                Sum(ss_ext_sales_price) ss_item_rev
         FROM   store_sales,
                item,
                date_dim
         WHERE  ss_item_sk = i_item_sk
                AND d_date IN (SELECT d_date
                               FROM   date_dim
                               WHERE  d_week_seq = (SELECT d_week_seq
                                                    FROM   date_dim
                                                    WHERE  d_date = '2002-02-25'
                                                   ))
                AND ss_sold_date_sk = d_date_sk
         GROUP  BY i_item_id),
     cs_items
     AS (SELECT i_item_id               item_id,
                Sum(cs_ext_sales_price) cs_item_rev
         FROM   catalog_sales,
                item,
                date_dim
         WHERE  cs_item_sk = i_item_sk
                AND d_date IN (SELECT d_date
                               FROM   date_dim
                               WHERE  d_week_seq = (SELECT d_week_seq
                                                    FROM   date_dim
                                                    WHERE  d_date = '2002-02-25'
                                                   ))
                AND cs_sold_date_sk = d_date_sk
         GROUP  BY i_item_id),
     ws_items
     AS (SELECT i_item_id               item_id,
                Sum(ws_ext_sales_price) ws_item_rev
         FROM   web_sales,
                item,
                date_dim
         WHERE  ws_item_sk = i_item_sk
                AND d_date IN (SELECT d_date
                               FROM   date_dim
                               WHERE  d_week_seq = (SELECT d_week_seq
                                                    FROM   date_dim
                                                    WHERE  d_date = '2002-02-25'
                                                   ))
                AND ws_sold_date_sk = d_date_sk
         GROUP  BY i_item_id)
SELECT ss_items.item_id,
               ss_item_rev,
               ss_item_rev / ( ss_item_rev + cs_item_rev + ws_item_rev ) / 3 *
               100 ss_dev,
               cs_item_rev,
               cs_item_rev / ( ss_item_rev + cs_item_rev + ws_item_rev ) / 3 *
               100 cs_dev,
               ws_item_rev,
               ws_item_rev / ( ss_item_rev + cs_item_rev + ws_item_rev ) / 3 *
               100 ws_dev,
               ( ss_item_rev + cs_item_rev + ws_item_rev ) / 3
               average
FROM   ss_items,
       cs_items,
       ws_items
WHERE  ss_items.item_id = cs_items.item_id
       AND ss_items.item_id = ws_items.item_id
       AND ss_item_rev BETWEEN 0.9 * cs_item_rev AND 1.1 * cs_item_rev
       AND ss_item_rev BETWEEN 0.9 * ws_item_rev AND 1.1 * ws_item_rev
       AND cs_item_rev BETWEEN 0.9 * ss_item_rev AND 1.1 * ss_item_rev
       AND cs_item_rev BETWEEN 0.9 * ws_item_rev AND 1.1 * ws_item_rev
       AND ws_item_rev BETWEEN 0.9 * ss_item_rev AND 1.1 * ss_item_rev
       AND ws_item_rev BETWEEN 0.9 * cs_item_rev AND 1.1 * cs_item_rev
ORDER  BY item_id,
          ss_item_rev
LIMIT 100;
WITH "item_2" AS (
  SELECT
    "item"."i_item_sk" AS "i_item_sk",
    "item"."i_item_id" AS "i_item_id"
  FROM "item" AS "item"
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_date" AS "d_date"
  FROM "date_dim" AS "date_dim"
), "_u_0" AS (
  SELECT
    "date_dim"."d_week_seq" AS "d_week_seq"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_date" = '2002-02-25'
), "_u_1" AS (
  SELECT
    "date_dim"."d_date" AS "d_date"
  FROM "date_dim" AS "date_dim"
  JOIN "_u_0" AS "_u_0"
    ON "_u_0"."d_week_seq" = "date_dim"."d_week_seq"
  GROUP BY
    "date_dim"."d_date"
), "ss_items" AS (
  SELECT
    "item"."i_item_id" AS "item_id",
    SUM("store_sales"."ss_ext_sales_price") AS "ss_item_rev"
  FROM "store_sales" AS "store_sales"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  LEFT JOIN "_u_1" AS "_u_1"
    ON "_u_1"."d_date" = "date_dim"."d_date"
  WHERE
    NOT "_u_1"."d_date" IS NULL
  GROUP BY
    "item"."i_item_id"
), "_u_3" AS (
  SELECT
    "date_dim"."d_date" AS "d_date"
  FROM "date_dim" AS "date_dim"
  JOIN "_u_0" AS "_u_2"
    ON "_u_2"."d_week_seq" = "date_dim"."d_week_seq"
  GROUP BY
    "date_dim"."d_date"
), "cs_items" AS (
  SELECT
    "item"."i_item_id" AS "item_id",
    SUM("catalog_sales"."cs_ext_sales_price") AS "cs_item_rev"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "item_2" AS "item"
    ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  LEFT JOIN "_u_3" AS "_u_3"
    ON "_u_3"."d_date" = "date_dim"."d_date"
  WHERE
    NOT "_u_3"."d_date" IS NULL
  GROUP BY
    "item"."i_item_id"
), "_u_5" AS (
  SELECT
    "date_dim"."d_date" AS "d_date"
  FROM "date_dim" AS "date_dim"
  JOIN "_u_0" AS "_u_4"
    ON "_u_4"."d_week_seq" = "date_dim"."d_week_seq"
  GROUP BY
    "date_dim"."d_date"
), "ws_items" AS (
  SELECT
    "item"."i_item_id" AS "item_id",
    SUM("web_sales"."ws_ext_sales_price") AS "ws_item_rev"
  FROM "web_sales" AS "web_sales"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "web_sales"."ws_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  LEFT JOIN "_u_5" AS "_u_5"
    ON "_u_5"."d_date" = "date_dim"."d_date"
  WHERE
    NOT "_u_5"."d_date" IS NULL
  GROUP BY
    "item"."i_item_id"
)
SELECT
  "ss_items"."item_id" AS "item_id",
  "ss_items"."ss_item_rev" AS "ss_item_rev",
  "ss_items"."ss_item_rev" / (
    "ss_items"."ss_item_rev" + "cs_items"."cs_item_rev" + "ws_items"."ws_item_rev"
  ) / 3 * 100 AS "ss_dev",
  "cs_items"."cs_item_rev" AS "cs_item_rev",
  "cs_items"."cs_item_rev" / (
    "ss_items"."ss_item_rev" + "cs_items"."cs_item_rev" + "ws_items"."ws_item_rev"
  ) / 3 * 100 AS "cs_dev",
  "ws_items"."ws_item_rev" AS "ws_item_rev",
  "ws_items"."ws_item_rev" / (
    "ss_items"."ss_item_rev" + "cs_items"."cs_item_rev" + "ws_items"."ws_item_rev"
  ) / 3 * 100 AS "ws_dev",
  (
    "ss_items"."ss_item_rev" + "cs_items"."cs_item_rev" + "ws_items"."ws_item_rev"
  ) / 3 AS "average"
FROM "ss_items" AS "ss_items"
JOIN "cs_items" AS "cs_items"
  ON "cs_items"."cs_item_rev" <= 1.1 * "ss_items"."ss_item_rev"
  AND "cs_items"."cs_item_rev" >= 0.9 * "ss_items"."ss_item_rev"
  AND "cs_items"."item_id" = "ss_items"."item_id"
  AND "ss_items"."ss_item_rev" <= 1.1 * "cs_items"."cs_item_rev"
  AND "ss_items"."ss_item_rev" >= 0.9 * "cs_items"."cs_item_rev"
JOIN "ws_items" AS "ws_items"
  ON "cs_items"."cs_item_rev" <= 1.1 * "ws_items"."ws_item_rev"
  AND "cs_items"."cs_item_rev" >= 0.9 * "ws_items"."ws_item_rev"
  AND "ss_items"."item_id" = "ws_items"."item_id"
  AND "ss_items"."ss_item_rev" <= 1.1 * "ws_items"."ws_item_rev"
  AND "ss_items"."ss_item_rev" >= 0.9 * "ws_items"."ws_item_rev"
  AND "ws_items"."ws_item_rev" <= 1.1 * "cs_items"."cs_item_rev"
  AND "ws_items"."ws_item_rev" <= 1.1 * "ss_items"."ss_item_rev"
  AND "ws_items"."ws_item_rev" >= 0.9 * "cs_items"."cs_item_rev"
  AND "ws_items"."ws_item_rev" >= 0.9 * "ss_items"."ss_item_rev"
ORDER BY
  "item_id",
  "ss_item_rev"
LIMIT 100;
