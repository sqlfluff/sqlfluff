--------------------------------------
-- TPC-DS 46
--------------------------------------
SELECT c_last_name,
               c_first_name,
               ca_city,
               bought_city,
               ss_ticket_number,
               amt,
               profit
FROM   (SELECT ss_ticket_number,
               ss_customer_sk,
               ca_city            bought_city,
               Sum(ss_coupon_amt) amt,
               Sum(ss_net_profit) profit
        FROM   store_sales,
               date_dim,
               store,
               household_demographics,
               customer_address
        WHERE  store_sales.ss_sold_date_sk = date_dim.d_date_sk
               AND store_sales.ss_store_sk = store.s_store_sk
               AND store_sales.ss_hdemo_sk = household_demographics.hd_demo_sk
               AND store_sales.ss_addr_sk = customer_address.ca_address_sk
               AND ( household_demographics.hd_dep_count = 6
                      OR household_demographics.hd_vehicle_count = 0 )
               AND date_dim.d_dow IN ( 6, 0 )
               AND date_dim.d_year IN ( 2000, 2000 + 1, 2000 + 2 )
               AND store.s_city IN ( 'Midway', 'Fairview', 'Fairview',
                                     'Fairview',
                                     'Fairview' )
        GROUP  BY ss_ticket_number,
                  ss_customer_sk,
                  ss_addr_sk,
                  ca_city) dn,
       customer,
       customer_address current_addr
WHERE  ss_customer_sk = c_customer_sk
       AND customer.c_current_addr_sk = current_addr.ca_address_sk
       AND current_addr.ca_city <> bought_city
ORDER  BY c_last_name,
          c_first_name,
          ca_city,
          bought_city,
          ss_ticket_number
LIMIT 100;
WITH "dn" AS (
  SELECT
    "store_sales"."ss_ticket_number" AS "ss_ticket_number",
    "store_sales"."ss_customer_sk" AS "ss_customer_sk",
    "customer_address"."ca_city" AS "bought_city",
    SUM("store_sales"."ss_coupon_amt") AS "amt",
    SUM("store_sales"."ss_net_profit") AS "profit"
  FROM "store_sales" AS "store_sales"
  JOIN "customer_address" AS "customer_address"
    ON "customer_address"."ca_address_sk" = "store_sales"."ss_addr_sk"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
    AND "date_dim"."d_dow" IN (6, 0)
    AND "date_dim"."d_year" IN (2000, 2001, 2002)
  JOIN "household_demographics" AS "household_demographics"
    ON "household_demographics"."hd_demo_sk" = "store_sales"."ss_hdemo_sk"
    AND (
      "household_demographics"."hd_dep_count" = 6
      OR "household_demographics"."hd_vehicle_count" = 0
    )
  JOIN "store" AS "store"
    ON "store"."s_city" IN ('Midway', 'Fairview', 'Fairview', 'Fairview', 'Fairview')
    AND "store"."s_store_sk" = "store_sales"."ss_store_sk"
  GROUP BY
    "store_sales"."ss_ticket_number",
    "store_sales"."ss_customer_sk",
    "store_sales"."ss_addr_sk",
    "customer_address"."ca_city"
)
SELECT
  "customer"."c_last_name" AS "c_last_name",
  "customer"."c_first_name" AS "c_first_name",
  "current_addr"."ca_city" AS "ca_city",
  "dn"."bought_city" AS "bought_city",
  "dn"."ss_ticket_number" AS "ss_ticket_number",
  "dn"."amt" AS "amt",
  "dn"."profit" AS "profit"
FROM "dn" AS "dn"
JOIN "customer" AS "customer"
  ON "customer"."c_customer_sk" = "dn"."ss_customer_sk"
JOIN "customer_address" AS "current_addr"
  ON "current_addr"."ca_address_sk" = "customer"."c_current_addr_sk"
  AND "current_addr"."ca_city" <> "dn"."bought_city"
ORDER BY
  "c_last_name",
  "c_first_name",
  "ca_city",
  "bought_city",
  "ss_ticket_number"
LIMIT 100;
