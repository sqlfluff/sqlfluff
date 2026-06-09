--------------------------------------
-- TPC-DS 95
--------------------------------------
WITH ws_wh AS
(
       SELECT ws1.ws_order_number,
              ws1.ws_warehouse_sk wh1,
              ws2.ws_warehouse_sk wh2
       FROM   web_sales ws1,
              web_sales ws2
       WHERE  ws1.ws_order_number = ws2.ws_order_number
       AND    ws1.ws_warehouse_sk <> ws2.ws_warehouse_sk)
SELECT
         Count(DISTINCT ws_order_number) AS "order count" ,
         Sum(ws_ext_ship_cost)           AS "total shipping cost" ,
         Sum(ws_net_profit)              AS "total net profit"
FROM     web_sales ws1 ,
         date_dim ,
         customer_address ,
         web_site
WHERE    d_date BETWEEN '2000-4-01' AND      (
                  Cast('2000-4-01' AS DATE) + INTERVAL '60' day)
AND      ws1.ws_ship_date_sk = d_date_sk
AND      ws1.ws_ship_addr_sk = ca_address_sk
AND      ca_state = 'IN'
AND      ws1.ws_web_site_sk = web_site_sk
AND      web_company_name = 'pri'
AND      ws1.ws_order_number IN
         (
                SELECT ws_order_number
                FROM   ws_wh)
AND      ws1.ws_order_number IN
         (
                SELECT wr_order_number
                FROM   web_returns,
                       ws_wh
                WHERE  wr_order_number = ws_wh.ws_order_number)
ORDER BY count(DISTINCT ws_order_number)
LIMIT 100;
WITH "ws_wh" AS (
  SELECT
    "ws1"."ws_order_number" AS "ws_order_number"
  FROM "web_sales" AS "ws1"
  JOIN "web_sales" AS "ws2"
    ON "ws1"."ws_order_number" = "ws2"."ws_order_number"
    AND "ws1"."ws_warehouse_sk" <> "ws2"."ws_warehouse_sk"
), "_u_0" AS (
  SELECT
    "ws_wh"."ws_order_number" AS "ws_order_number"
  FROM "ws_wh" AS "ws_wh"
  GROUP BY
    "ws_wh"."ws_order_number"
), "_u_1" AS (
  SELECT
    "web_returns"."wr_order_number" AS "wr_order_number"
  FROM "web_returns" AS "web_returns"
  JOIN "ws_wh" AS "ws_wh"
    ON "web_returns"."wr_order_number" = "ws_wh"."ws_order_number"
  GROUP BY
    "web_returns"."wr_order_number"
)
SELECT
  COUNT(DISTINCT "ws1"."ws_order_number") AS "order count",
  SUM("ws1"."ws_ext_ship_cost") AS "total shipping cost",
  SUM("ws1"."ws_net_profit") AS "total net profit"
FROM "web_sales" AS "ws1"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date" >= '2000-4-01'
  AND "date_dim"."d_date_sk" = "ws1"."ws_ship_date_sk"
  AND (
    CAST('2000-4-01' AS DATE) + INTERVAL '60' DAY
  ) >= CAST("date_dim"."d_date" AS DATE)
JOIN "customer_address" AS "customer_address"
  ON "customer_address"."ca_address_sk" = "ws1"."ws_ship_addr_sk"
  AND "customer_address"."ca_state" = 'IN'
JOIN "web_site" AS "web_site"
  ON "web_site"."web_company_name" = 'pri'
  AND "web_site"."web_site_sk" = "ws1"."ws_web_site_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."ws_order_number" = "ws1"."ws_order_number"
LEFT JOIN "_u_1" AS "_u_1"
  ON "_u_1"."wr_order_number" = "ws1"."ws_order_number"
WHERE
  NOT "_u_0"."ws_order_number" IS NULL AND NOT "_u_1"."wr_order_number" IS NULL
ORDER BY
  COUNT(DISTINCT "ws1"."ws_order_number")
LIMIT 100;
