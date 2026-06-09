--------------------------------------
-- TPC-DS 40
--------------------------------------
SELECT
                w_state ,
                i_item_id ,
                Sum(
                CASE
                                WHEN (
                                                                Cast(d_date AS DATE) < Cast ('2002-06-01' AS DATE)) THEN cs_sales_price - COALESCE(cr_refunded_cash,0)
                                ELSE 0
                END) AS sales_before ,
                Sum(
                CASE
                                WHEN (
                                                                Cast(d_date AS DATE) >= Cast ('2002-06-01' AS DATE)) THEN cs_sales_price - COALESCE(cr_refunded_cash,0)
                                ELSE 0
                END) AS sales_after
FROM            catalog_sales
LEFT OUTER JOIN catalog_returns
ON              (
                                cs_order_number = cr_order_number
                AND             cs_item_sk = cr_item_sk) ,
                warehouse ,
                item ,
                date_dim
WHERE           i_current_price BETWEEN 0.99 AND             1.49
AND             i_item_sk = cs_item_sk
AND             cs_warehouse_sk = w_warehouse_sk
AND             cs_sold_date_sk = d_date_sk
AND             d_date BETWEEN (Cast ('2002-06-01' AS DATE) - INTERVAL '30' day) AND             (
                                cast ('2002-06-01' AS date) + INTERVAL '30' day)
GROUP BY        w_state,
                i_item_id
ORDER BY        w_state,
                i_item_id
LIMIT 100;
SELECT
  "warehouse"."w_state" AS "w_state",
  "item"."i_item_id" AS "i_item_id",
  SUM(
    CASE
      WHEN CAST("date_dim"."d_date" AS DATE) < CAST('2002-06-01' AS DATE)
      THEN "catalog_sales"."cs_sales_price" - COALESCE("catalog_returns"."cr_refunded_cash", 0)
      ELSE 0
    END
  ) AS "sales_before",
  SUM(
    CASE
      WHEN CAST("date_dim"."d_date" AS DATE) >= CAST('2002-06-01' AS DATE)
      THEN "catalog_sales"."cs_sales_price" - COALESCE("catalog_returns"."cr_refunded_cash", 0)
      ELSE 0
    END
  ) AS "sales_after"
FROM "catalog_sales" AS "catalog_sales"
LEFT JOIN "catalog_returns" AS "catalog_returns"
  ON "catalog_returns"."cr_item_sk" = "catalog_sales"."cs_item_sk"
  AND "catalog_returns"."cr_order_number" = "catalog_sales"."cs_order_number"
JOIN "warehouse" AS "warehouse"
  ON "catalog_sales"."cs_warehouse_sk" = "warehouse"."w_warehouse_sk"
JOIN "item" AS "item"
  ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
  AND "item"."i_current_price" <= 1.49
  AND "item"."i_current_price" >= 0.99
JOIN "date_dim" AS "date_dim"
  ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  AND CAST("date_dim"."d_date" AS DATE) <= CAST('2002-07-01' AS DATE)
  AND CAST("date_dim"."d_date" AS DATE) >= CAST('2002-05-02' AS DATE)
GROUP BY
  "warehouse"."w_state",
  "item"."i_item_id"
ORDER BY
  "w_state",
  "i_item_id"
LIMIT 100;
