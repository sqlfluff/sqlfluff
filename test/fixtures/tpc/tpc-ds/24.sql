--------------------------------------
-- TPC-DS 24
--------------------------------------
WITH ssales
     AS (SELECT c_last_name,
                c_first_name,
                s_store_name,
                ca_state,
                s_state,
                i_color,
                i_current_price,
                i_manager_id,
                i_units,
                i_size,
                Sum(ss_net_profit) netpaid
         FROM   store_sales,
                store_returns,
                store,
                item,
                customer,
                customer_address
         WHERE  ss_ticket_number = sr_ticket_number
                AND ss_item_sk = sr_item_sk
                AND ss_customer_sk = c_customer_sk
                AND ss_item_sk = i_item_sk
                AND ss_store_sk = s_store_sk
                AND c_birth_country = Upper(ca_country)
                AND s_zip = ca_zip
                AND s_market_id = 6
         GROUP  BY c_last_name,
                   c_first_name,
                   s_store_name,
                   ca_state,
                   s_state,
                   i_color,
                   i_current_price,
                   i_manager_id,
                   i_units,
                   i_size)
SELECT c_last_name,
       c_first_name,
       s_store_name,
       Sum(netpaid) paid
FROM   ssales
WHERE  i_color = 'papaya'
GROUP  BY c_last_name,
          c_first_name,
          s_store_name
HAVING Sum(netpaid) > (SELECT 0.05 * Avg(netpaid)
                       FROM   ssales);
WITH "ssales" AS (
  SELECT
    "customer"."c_last_name" AS "c_last_name",
    "customer"."c_first_name" AS "c_first_name",
    "store"."s_store_name" AS "s_store_name",
    "item"."i_color" AS "i_color",
    SUM("store_sales"."ss_net_profit") AS "netpaid"
  FROM "store_sales" AS "store_sales"
  JOIN "customer" AS "customer"
    ON "customer"."c_customer_sk" = "store_sales"."ss_customer_sk"
  JOIN "item" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "store" AS "store"
    ON "store"."s_market_id" = 6 AND "store"."s_store_sk" = "store_sales"."ss_store_sk"
  JOIN "store_returns" AS "store_returns"
    ON "store_returns"."sr_item_sk" = "store_sales"."ss_item_sk"
    AND "store_returns"."sr_ticket_number" = "store_sales"."ss_ticket_number"
  JOIN "customer_address" AS "customer_address"
    ON "customer"."c_birth_country" = UPPER("customer_address"."ca_country")
    AND "customer_address"."ca_zip" = "store"."s_zip"
  GROUP BY
    "customer"."c_last_name",
    "customer"."c_first_name",
    "store"."s_store_name",
    "customer_address"."ca_state",
    "store"."s_state",
    "item"."i_color",
    "item"."i_current_price",
    "item"."i_manager_id",
    "item"."i_units",
    "item"."i_size"
), "_u_0" AS (
  SELECT
    0.05 * AVG("ssales"."netpaid") AS "_col_0"
  FROM "ssales" AS "ssales"
)
SELECT
  "ssales"."c_last_name" AS "c_last_name",
  "ssales"."c_first_name" AS "c_first_name",
  "ssales"."s_store_name" AS "s_store_name",
  SUM("ssales"."netpaid") AS "paid"
FROM "ssales" AS "ssales"
CROSS JOIN "_u_0" AS "_u_0"
WHERE
  "ssales"."i_color" = 'papaya'
GROUP BY
  "ssales"."c_last_name",
  "ssales"."c_first_name",
  "ssales"."s_store_name"
HAVING
  MAX("_u_0"."_col_0") < SUM("ssales"."netpaid");
