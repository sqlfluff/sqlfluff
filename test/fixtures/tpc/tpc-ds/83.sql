--------------------------------------
-- TPC-DS 83
--------------------------------------
WITH sr_items
     AS (SELECT i_item_id               item_id,
                Sum(sr_return_quantity) sr_item_qty
         FROM   store_returns,
                item,
                date_dim
         WHERE  sr_item_sk = i_item_sk
                AND d_date IN (SELECT d_date
                               FROM   date_dim
                               WHERE  d_week_seq IN (SELECT d_week_seq
                                                     FROM   date_dim
                                                     WHERE
                                      d_date IN ( '1999-06-30',
                                                  '1999-08-28',
                                                  '1999-11-18'
                                                )))
                AND sr_returned_date_sk = d_date_sk
         GROUP  BY i_item_id),
     cr_items
     AS (SELECT i_item_id               item_id,
                Sum(cr_return_quantity) cr_item_qty
         FROM   catalog_returns,
                item,
                date_dim
         WHERE  cr_item_sk = i_item_sk
                AND d_date IN (SELECT d_date
                               FROM   date_dim
                               WHERE  d_week_seq IN (SELECT d_week_seq
                                                     FROM   date_dim
                                                     WHERE
                                      d_date IN ( '1999-06-30',
                                                  '1999-08-28',
                                                  '1999-11-18'
                                                )))
                AND cr_returned_date_sk = d_date_sk
         GROUP  BY i_item_id),
     wr_items
     AS (SELECT i_item_id               item_id,
                Sum(wr_return_quantity) wr_item_qty
         FROM   web_returns,
                item,
                date_dim
         WHERE  wr_item_sk = i_item_sk
                AND d_date IN (SELECT d_date
                               FROM   date_dim
                               WHERE  d_week_seq IN (SELECT d_week_seq
                                                     FROM   date_dim
                                                     WHERE
                                      d_date IN ( '1999-06-30',
                                                  '1999-08-28',
                                                  '1999-11-18'
                                                )))
                AND wr_returned_date_sk = d_date_sk
         GROUP  BY i_item_id)
SELECT sr_items.item_id,
               sr_item_qty,
               sr_item_qty / ( sr_item_qty + cr_item_qty + wr_item_qty ) / 3.0 *
               100 sr_dev,
               cr_item_qty,
               cr_item_qty / ( sr_item_qty + cr_item_qty + wr_item_qty ) / 3.0 *
               100 cr_dev,
               wr_item_qty,
               wr_item_qty / ( sr_item_qty + cr_item_qty + wr_item_qty ) / 3.0 *
               100 wr_dev,
               ( sr_item_qty + cr_item_qty + wr_item_qty ) / 3.0
               average
FROM   sr_items,
       cr_items,
       wr_items
WHERE  sr_items.item_id = cr_items.item_id
       AND sr_items.item_id = wr_items.item_id
ORDER  BY sr_items.item_id,
          sr_item_qty
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
    "date_dim"."d_date" IN ('1999-06-30', '1999-08-28', '1999-11-18')
  GROUP BY
    "date_dim"."d_week_seq"
), "_u_1" AS (
  SELECT
    "date_dim"."d_date" AS "d_date"
  FROM "date_dim" AS "date_dim"
  LEFT JOIN "_u_0" AS "_u_0"
    ON "_u_0"."d_week_seq" = "date_dim"."d_week_seq"
  WHERE
    NOT "_u_0"."d_week_seq" IS NULL
  GROUP BY
    "date_dim"."d_date"
), "sr_items" AS (
  SELECT
    "item"."i_item_id" AS "item_id",
    SUM("store_returns"."sr_return_quantity") AS "sr_item_qty"
  FROM "store_returns" AS "store_returns"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "store_returns"."sr_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_returns"."sr_returned_date_sk"
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
  LEFT JOIN "_u_0" AS "_u_2"
    ON "_u_2"."d_week_seq" = "date_dim"."d_week_seq"
  WHERE
    NOT "_u_2"."d_week_seq" IS NULL
  GROUP BY
    "date_dim"."d_date"
), "cr_items" AS (
  SELECT
    "item"."i_item_id" AS "item_id",
    SUM("catalog_returns"."cr_return_quantity") AS "cr_item_qty"
  FROM "catalog_returns" AS "catalog_returns"
  JOIN "item_2" AS "item"
    ON "catalog_returns"."cr_item_sk" = "item"."i_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_returns"."cr_returned_date_sk" = "date_dim"."d_date_sk"
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
  LEFT JOIN "_u_0" AS "_u_4"
    ON "_u_4"."d_week_seq" = "date_dim"."d_week_seq"
  WHERE
    NOT "_u_4"."d_week_seq" IS NULL
  GROUP BY
    "date_dim"."d_date"
), "wr_items" AS (
  SELECT
    "item"."i_item_id" AS "item_id",
    SUM("web_returns"."wr_return_quantity") AS "wr_item_qty"
  FROM "web_returns" AS "web_returns"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "web_returns"."wr_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_returns"."wr_returned_date_sk"
  LEFT JOIN "_u_5" AS "_u_5"
    ON "_u_5"."d_date" = "date_dim"."d_date"
  WHERE
    NOT "_u_5"."d_date" IS NULL
  GROUP BY
    "item"."i_item_id"
)
SELECT
  "sr_items"."item_id" AS "item_id",
  "sr_items"."sr_item_qty" AS "sr_item_qty",
  "sr_items"."sr_item_qty" / (
    "sr_items"."sr_item_qty" + "cr_items"."cr_item_qty" + "wr_items"."wr_item_qty"
  ) / 3.0 * 100 AS "sr_dev",
  "cr_items"."cr_item_qty" AS "cr_item_qty",
  "cr_items"."cr_item_qty" / (
    "sr_items"."sr_item_qty" + "cr_items"."cr_item_qty" + "wr_items"."wr_item_qty"
  ) / 3.0 * 100 AS "cr_dev",
  "wr_items"."wr_item_qty" AS "wr_item_qty",
  "wr_items"."wr_item_qty" / (
    "sr_items"."sr_item_qty" + "cr_items"."cr_item_qty" + "wr_items"."wr_item_qty"
  ) / 3.0 * 100 AS "wr_dev",
  (
    "sr_items"."sr_item_qty" + "cr_items"."cr_item_qty" + "wr_items"."wr_item_qty"
  ) / 3.0 AS "average"
FROM "sr_items" AS "sr_items"
JOIN "cr_items" AS "cr_items"
  ON "cr_items"."item_id" = "sr_items"."item_id"
JOIN "wr_items" AS "wr_items"
  ON "sr_items"."item_id" = "wr_items"."item_id"
ORDER BY
  "sr_items"."item_id",
  "sr_item_qty"
LIMIT 100;
