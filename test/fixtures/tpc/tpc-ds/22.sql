--------------------------------------
-- TPC-DS 22
--------------------------------------
SELECT i_product_name,
               i_brand,
               i_class,
               i_category,
               Avg(inv_quantity_on_hand) qoh
FROM   inventory,
       date_dim,
       item,
       warehouse
WHERE  inv_date_sk = d_date_sk
       AND inv_item_sk = i_item_sk
       AND inv_warehouse_sk = w_warehouse_sk
       AND d_month_seq BETWEEN 1205 AND 1205 + 11
GROUP  BY rollup( i_product_name, i_brand, i_class, i_category )
ORDER  BY qoh,
          i_product_name,
          i_brand,
          i_class,
          i_category
LIMIT 100;
SELECT
  "item"."i_product_name" AS "i_product_name",
  "item"."i_brand" AS "i_brand",
  "item"."i_class" AS "i_class",
  "item"."i_category" AS "i_category",
  AVG("inventory"."inv_quantity_on_hand") AS "qoh"
FROM "inventory" AS "inventory"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "inventory"."inv_date_sk"
  AND "date_dim"."d_month_seq" <= 1216
  AND "date_dim"."d_month_seq" >= 1205
JOIN "item" AS "item"
  ON "inventory"."inv_item_sk" = "item"."i_item_sk"
JOIN "warehouse" AS "warehouse"
  ON "inventory"."inv_warehouse_sk" = "warehouse"."w_warehouse_sk"
GROUP BY
  ROLLUP (
    "item"."i_product_name",
    "item"."i_brand",
    "item"."i_class",
    "item"."i_category"
  )
ORDER BY
  "qoh",
  "i_product_name",
  "i_brand",
  "i_class",
  "i_category"
LIMIT 100;
