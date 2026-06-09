--------------------------------------
-- TPC-DS 82
--------------------------------------
SELECT
         i_item_id ,
         i_item_desc ,
         i_current_price
FROM     item,
         inventory,
         date_dim,
         store_sales
WHERE    i_current_price BETWEEN 63 AND      63+30
AND      inv_item_sk = i_item_sk
AND      d_date_sk=inv_date_sk
AND      d_date BETWEEN Cast('1998-04-27' AS DATE) AND      (
                  Cast('1998-04-27' AS DATE) + INTERVAL '60' day)
AND      i_manufact_id IN (57,293,427,320)
AND      inv_quantity_on_hand BETWEEN 100 AND      500
AND      ss_item_sk = i_item_sk
GROUP BY i_item_id,
         i_item_desc,
         i_current_price
ORDER BY i_item_id
LIMIT 100;
SELECT
  "item"."i_item_id" AS "i_item_id",
  "item"."i_item_desc" AS "i_item_desc",
  "item"."i_current_price" AS "i_current_price"
FROM "item" AS "item"
JOIN "inventory" AS "inventory"
  ON "inventory"."inv_item_sk" = "item"."i_item_sk"
  AND "inventory"."inv_quantity_on_hand" <= 500
  AND "inventory"."inv_quantity_on_hand" >= 100
JOIN "store_sales" AS "store_sales"
  ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "inventory"."inv_date_sk"
  AND CAST("date_dim"."d_date" AS DATE) <= CAST('1998-06-26' AS DATE)
  AND CAST("date_dim"."d_date" AS DATE) >= CAST('1998-04-27' AS DATE)
WHERE
  "item"."i_current_price" <= 93
  AND "item"."i_current_price" >= 63
  AND "item"."i_manufact_id" IN (57, 293, 427, 320)
GROUP BY
  "item"."i_item_id",
  "item"."i_item_desc",
  "item"."i_current_price"
ORDER BY
  "i_item_id"
LIMIT 100;
