--------------------------------------
-- TPC-DS 21
--------------------------------------
SELECT
         *
FROM    (
                  SELECT   w_warehouse_name ,
                           i_item_id ,
                           Sum(
                           CASE
                                    WHEN (
                                                      Cast(d_date AS DATE) < Cast ('2000-05-13' AS DATE)) THEN inv_quantity_on_hand
                                    ELSE 0
                           END) AS inv_before ,
                           Sum(
                           CASE
                                    WHEN (
                                                      Cast(d_date AS DATE) >= Cast ('2000-05-13' AS DATE)) THEN inv_quantity_on_hand
                                    ELSE 0
                           END) AS inv_after
                  FROM     inventory ,
                           warehouse ,
                           item ,
                           date_dim
                  WHERE    i_current_price BETWEEN 0.99 AND      1.49
                  AND      i_item_sk = inv_item_sk
                  AND      inv_warehouse_sk = w_warehouse_sk
                  AND      inv_date_sk = d_date_sk
                  AND      d_date BETWEEN (Cast ('2000-05-13' AS DATE) - INTERVAL '30' day) AND      (
                                    cast ('2000-05-13' AS        date) + INTERVAL '30' day)
                  GROUP BY w_warehouse_name,
                           i_item_id) x
WHERE    (
                  CASE
                           WHEN inv_before > 0 THEN inv_after / inv_before
                           ELSE NULL
                  END) BETWEEN 2.0/3.0 AND      3.0/2.0
ORDER BY w_warehouse_name ,
         i_item_id
LIMIT 100;
WITH "x" AS (
  SELECT
    "warehouse"."w_warehouse_name" AS "w_warehouse_name",
    "item"."i_item_id" AS "i_item_id",
    SUM(
      CASE
        WHEN CAST("date_dim"."d_date" AS DATE) < CAST('2000-05-13' AS DATE)
        THEN "inventory"."inv_quantity_on_hand"
        ELSE 0
      END
    ) AS "inv_before",
    SUM(
      CASE
        WHEN CAST("date_dim"."d_date" AS DATE) >= CAST('2000-05-13' AS DATE)
        THEN "inventory"."inv_quantity_on_hand"
        ELSE 0
      END
    ) AS "inv_after"
  FROM "inventory" AS "inventory"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "inventory"."inv_date_sk"
    AND CAST("date_dim"."d_date" AS DATE) <= CAST('2000-06-12' AS DATE)
    AND CAST("date_dim"."d_date" AS DATE) >= CAST('2000-04-13' AS DATE)
  JOIN "item" AS "item"
    ON "inventory"."inv_item_sk" = "item"."i_item_sk"
    AND "item"."i_current_price" <= 1.49
    AND "item"."i_current_price" >= 0.99
  JOIN "warehouse" AS "warehouse"
    ON "inventory"."inv_warehouse_sk" = "warehouse"."w_warehouse_sk"
  GROUP BY
    "warehouse"."w_warehouse_name",
    "item"."i_item_id"
)
SELECT
  "x"."w_warehouse_name" AS "w_warehouse_name",
  "x"."i_item_id" AS "i_item_id",
  "x"."inv_before" AS "inv_before",
  "x"."inv_after" AS "inv_after"
FROM "x" AS "x"
WHERE
  CASE WHEN "x"."inv_before" > 0 THEN "x"."inv_after" / "x"."inv_before" ELSE NULL END <= 1.5
  AND CASE WHEN "x"."inv_before" > 0 THEN "x"."inv_after" / "x"."inv_before" ELSE NULL END >= 0.6666666666666666666666666667
ORDER BY
  "x"."w_warehouse_name",
  "x"."i_item_id"
LIMIT 100;
