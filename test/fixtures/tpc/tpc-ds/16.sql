--------------------------------------
-- TPC-DS 16
--------------------------------------
SELECT
         Count(DISTINCT cs_order_number) AS "order count" ,
         Sum(cs_ext_ship_cost)           AS "total shipping cost" ,
         Sum(cs_net_profit)              AS "total net profit"
FROM     catalog_sales cs1 ,
         date_dim ,
         customer_address ,
         call_center
WHERE    d_date BETWEEN '2002-3-01' AND      (
                  Cast('2002-3-01' AS DATE) + INTERVAL '60' day)
AND      cs1.cs_ship_date_sk = d_date_sk
AND      cs1.cs_ship_addr_sk = ca_address_sk
AND      ca_state = 'IA'
AND      cs1.cs_call_center_sk = cc_call_center_sk
AND      cc_county IN ('Williamson County',
                       'Williamson County',
                       'Williamson County',
                       'Williamson County',
                       'Williamson County' )
AND      EXISTS
         (
                SELECT *
                FROM   catalog_sales cs2
                WHERE  cs1.cs_order_number = cs2.cs_order_number
                AND    cs1.cs_warehouse_sk <> cs2.cs_warehouse_sk)
AND      NOT EXISTS
         (
                SELECT *
                FROM   catalog_returns cr1
                WHERE  cs1.cs_order_number = cr1.cr_order_number)
ORDER BY count(DISTINCT cs_order_number)
LIMIT 100;
WITH "_u_0" AS (
  SELECT
    "cs2"."cs_order_number" AS "_u_1",
    ARRAY_AGG("cs2"."cs_warehouse_sk") AS "_u_2"
  FROM "catalog_sales" AS "cs2"
  GROUP BY
    "cs2"."cs_order_number"
), "_u_3" AS (
  SELECT
    "cr1"."cr_order_number" AS "_u_4"
  FROM "catalog_returns" AS "cr1"
  GROUP BY
    "cr1"."cr_order_number"
)
SELECT
  COUNT(DISTINCT "cs1"."cs_order_number") AS "order count",
  SUM("cs1"."cs_ext_ship_cost") AS "total shipping cost",
  SUM("cs1"."cs_net_profit") AS "total net profit"
FROM "catalog_sales" AS "cs1"
JOIN "date_dim" AS "date_dim"
  ON "cs1"."cs_ship_date_sk" = "date_dim"."d_date_sk"
  AND "date_dim"."d_date" >= '2002-3-01'
  AND (
    CAST('2002-3-01' AS DATE) + INTERVAL '60' DAY
  ) >= CAST("date_dim"."d_date" AS DATE)
JOIN "customer_address" AS "customer_address"
  ON "cs1"."cs_ship_addr_sk" = "customer_address"."ca_address_sk"
  AND "customer_address"."ca_state" = 'IA'
JOIN "call_center" AS "call_center"
  ON "call_center"."cc_call_center_sk" = "cs1"."cs_call_center_sk"
  AND "call_center"."cc_county" IN (
    'Williamson County',
    'Williamson County',
    'Williamson County',
    'Williamson County',
    'Williamson County'
  )
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "cs1"."cs_order_number"
LEFT JOIN "_u_3" AS "_u_3"
  ON "_u_3"."_u_4" = "cs1"."cs_order_number"
WHERE
  "_u_3"."_u_4" IS NULL
  AND ARRAY_ANY("_u_0"."_u_2", "_x" -> "cs1"."cs_warehouse_sk" <> "_x")
  AND NOT "_u_0"."_u_1" IS NULL
ORDER BY
  COUNT(DISTINCT "cs1"."cs_order_number")
LIMIT 100;
