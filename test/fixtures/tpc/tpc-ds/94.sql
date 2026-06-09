--------------------------------------
-- TPC-DS 94
--------------------------------------
SELECT
         Count(DISTINCT ws_order_number) AS "order count" ,
         Sum(ws_ext_ship_cost)           AS "total shipping cost" ,
         Sum(ws_net_profit)              AS "total net profit"
FROM     web_sales ws1 ,
         date_dim ,
         customer_address ,
         web_site
WHERE    d_date BETWEEN '2000-3-01' AND      (
                  Cast('2000-3-01' AS DATE) + INTERVAL '60' day)
AND      ws1.ws_ship_date_sk = d_date_sk
AND      ws1.ws_ship_addr_sk = ca_address_sk
AND      ca_state = 'MT'
AND      ws1.ws_web_site_sk = web_site_sk
AND      web_company_name = 'pri'
AND      EXISTS
         (
                SELECT *
                FROM   web_sales ws2
                WHERE  ws1.ws_order_number = ws2.ws_order_number
                AND    ws1.ws_warehouse_sk <> ws2.ws_warehouse_sk)
AND      NOT EXISTS
         (
                SELECT *
                FROM   web_returns wr1
                WHERE  ws1.ws_order_number = wr1.wr_order_number)
ORDER BY count(DISTINCT ws_order_number)
LIMIT 100;
WITH "_u_0" AS (
  SELECT
    "ws2"."ws_order_number" AS "_u_1",
    ARRAY_AGG("ws2"."ws_warehouse_sk") AS "_u_2"
  FROM "web_sales" AS "ws2"
  GROUP BY
    "ws2"."ws_order_number"
), "_u_3" AS (
  SELECT
    "wr1"."wr_order_number" AS "_u_4"
  FROM "web_returns" AS "wr1"
  GROUP BY
    "wr1"."wr_order_number"
)
SELECT
  COUNT(DISTINCT "ws1"."ws_order_number") AS "order count",
  SUM("ws1"."ws_ext_ship_cost") AS "total shipping cost",
  SUM("ws1"."ws_net_profit") AS "total net profit"
FROM "web_sales" AS "ws1"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date" >= '2000-3-01'
  AND "date_dim"."d_date_sk" = "ws1"."ws_ship_date_sk"
  AND (
    CAST('2000-3-01' AS DATE) + INTERVAL '60' DAY
  ) >= CAST("date_dim"."d_date" AS DATE)
JOIN "customer_address" AS "customer_address"
  ON "customer_address"."ca_address_sk" = "ws1"."ws_ship_addr_sk"
  AND "customer_address"."ca_state" = 'MT'
JOIN "web_site" AS "web_site"
  ON "web_site"."web_company_name" = 'pri'
  AND "web_site"."web_site_sk" = "ws1"."ws_web_site_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "ws1"."ws_order_number"
LEFT JOIN "_u_3" AS "_u_3"
  ON "_u_3"."_u_4" = "ws1"."ws_order_number"
WHERE
  "_u_3"."_u_4" IS NULL
  AND ARRAY_ANY("_u_0"."_u_2", "_x" -> "ws1"."ws_warehouse_sk" <> "_x")
  AND NOT "_u_0"."_u_1" IS NULL
ORDER BY
  COUNT(DISTINCT "ws1"."ws_order_number")
LIMIT 100;
