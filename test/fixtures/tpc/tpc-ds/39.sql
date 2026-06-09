--------------------------------------
-- TPC-DS 39
--------------------------------------
WITH inv
     AS (SELECT w_warehouse_name,
                w_warehouse_sk,
                i_item_sk,
                d_moy,
                stdev,
                mean,
                CASE mean
                  WHEN 0 THEN NULL
                  ELSE stdev / mean
                END cov
         FROM  (SELECT w_warehouse_name,
                       w_warehouse_sk,
                       i_item_sk,
                       d_moy,
                       Stddev_samp(inv_quantity_on_hand) stdev,
                       Avg(inv_quantity_on_hand)         mean
                FROM   inventory,
                       item,
                       warehouse,
                       date_dim
                WHERE  inv_item_sk = i_item_sk
                       AND inv_warehouse_sk = w_warehouse_sk
                       AND inv_date_sk = d_date_sk
                       AND d_year = 2002
                GROUP  BY w_warehouse_name,
                          w_warehouse_sk,
                          i_item_sk,
                          d_moy) foo
         WHERE  CASE mean
                  WHEN 0 THEN 0
                  ELSE stdev / mean
                END > 1)
SELECT inv1.w_warehouse_sk,
       inv1.i_item_sk,
       inv1.d_moy,
       inv1.mean,
       inv1.cov,
       inv2.w_warehouse_sk,
       inv2.i_item_sk,
       inv2.d_moy,
       inv2.mean,
       inv2.cov
FROM   inv inv1,
       inv inv2
WHERE  inv1.i_item_sk = inv2.i_item_sk
       AND inv1.w_warehouse_sk = inv2.w_warehouse_sk
       AND inv1.d_moy = 1
       AND inv2.d_moy = 1 + 1
ORDER  BY inv1.w_warehouse_sk,
          inv1.i_item_sk,
          inv1.d_moy,
          inv1.mean,
          inv1.cov,
          inv2.d_moy,
          inv2.mean,
          inv2.cov;
WITH "foo" AS (
  SELECT
    "warehouse"."w_warehouse_sk" AS "w_warehouse_sk",
    "item"."i_item_sk" AS "i_item_sk",
    "date_dim"."d_moy" AS "d_moy",
    STDDEV_SAMP("inventory"."inv_quantity_on_hand") AS "stdev",
    AVG("inventory"."inv_quantity_on_hand") AS "mean"
  FROM "inventory" AS "inventory"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "inventory"."inv_date_sk" AND "date_dim"."d_year" = 2002
  JOIN "item" AS "item"
    ON "inventory"."inv_item_sk" = "item"."i_item_sk"
  JOIN "warehouse" AS "warehouse"
    ON "inventory"."inv_warehouse_sk" = "warehouse"."w_warehouse_sk"
  GROUP BY
    "warehouse"."w_warehouse_name",
    "warehouse"."w_warehouse_sk",
    "item"."i_item_sk",
    "date_dim"."d_moy"
), "inv" AS (
  SELECT
    "foo"."w_warehouse_sk" AS "w_warehouse_sk",
    "foo"."i_item_sk" AS "i_item_sk",
    "foo"."d_moy" AS "d_moy",
    "foo"."mean" AS "mean",
    CASE WHEN "foo"."mean" = 0 THEN NULL ELSE "foo"."stdev" / "foo"."mean" END AS "cov"
  FROM "foo" AS "foo"
  WHERE
    CASE WHEN "foo"."mean" = 0 THEN 0 ELSE "foo"."stdev" / "foo"."mean" END > 1
)
SELECT
  "inv1"."w_warehouse_sk" AS "w_warehouse_sk",
  "inv1"."i_item_sk" AS "i_item_sk",
  "inv1"."d_moy" AS "d_moy",
  "inv1"."mean" AS "mean",
  "inv1"."cov" AS "cov",
  "inv2"."w_warehouse_sk" AS "w_warehouse_sk",
  "inv2"."i_item_sk" AS "i_item_sk",
  "inv2"."d_moy" AS "d_moy",
  "inv2"."mean" AS "mean",
  "inv2"."cov" AS "cov"
FROM "inv" AS "inv1"
JOIN "inv" AS "inv2"
  ON "inv1"."i_item_sk" = "inv2"."i_item_sk"
  AND "inv1"."w_warehouse_sk" = "inv2"."w_warehouse_sk"
  AND "inv2"."d_moy" = 2
WHERE
  "inv1"."d_moy" = 1
ORDER BY
  "inv1"."w_warehouse_sk",
  "inv1"."i_item_sk",
  "inv1"."d_moy",
  "inv1"."mean",
  "inv1"."cov",
  "inv2"."d_moy",
  "inv2"."mean",
  "inv2"."cov";
