--------------------------------------
-- TPC-DS 84
--------------------------------------
SELECT c_customer_id   AS customer_id,
               c_last_name
               || ', '
               || c_first_name AS customername
FROM   customer,
       customer_address,
       customer_demographics,
       household_demographics,
       income_band,
       store_returns
WHERE  ca_city = 'Green Acres'
       AND c_current_addr_sk = ca_address_sk
       AND ib_lower_bound >= 54986
       AND ib_upper_bound <= 54986 + 50000
       AND ib_income_band_sk = hd_income_band_sk
       AND cd_demo_sk = c_current_cdemo_sk
       AND hd_demo_sk = c_current_hdemo_sk
       AND sr_cdemo_sk = cd_demo_sk
ORDER  BY c_customer_id
LIMIT 100;
SELECT
  "customer"."c_customer_id" AS "customer_id",
  "customer"."c_last_name" || ', ' || "customer"."c_first_name" AS "customername"
FROM "customer" AS "customer"
JOIN "customer_address" AS "customer_address"
  ON "customer"."c_current_addr_sk" = "customer_address"."ca_address_sk"
  AND "customer_address"."ca_city" = 'Green Acres'
JOIN "customer_demographics" AS "customer_demographics"
  ON "customer"."c_current_cdemo_sk" = "customer_demographics"."cd_demo_sk"
JOIN "household_demographics" AS "household_demographics"
  ON "customer"."c_current_hdemo_sk" = "household_demographics"."hd_demo_sk"
JOIN "income_band" AS "income_band"
  ON "household_demographics"."hd_income_band_sk" = "income_band"."ib_income_band_sk"
  AND "income_band"."ib_lower_bound" >= 54986
  AND "income_band"."ib_upper_bound" <= 104986
JOIN "store_returns" AS "store_returns"
  ON "customer_demographics"."cd_demo_sk" = "store_returns"."sr_cdemo_sk"
ORDER BY
  "customer"."c_customer_id"
LIMIT 100;
