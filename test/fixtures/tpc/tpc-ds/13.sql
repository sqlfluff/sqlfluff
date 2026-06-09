--------------------------------------
-- TPC-DS 13
--------------------------------------
SELECT Avg(ss_quantity),
       Avg(ss_ext_sales_price),
       Avg(ss_ext_wholesale_cost),
       Sum(ss_ext_wholesale_cost)
FROM   store_sales,
       store,
       customer_demographics,
       household_demographics,
       customer_address,
       date_dim
WHERE  s_store_sk = ss_store_sk
       AND ss_sold_date_sk = d_date_sk
       AND d_year = 2001
       AND ( ( ss_hdemo_sk = hd_demo_sk
               AND cd_demo_sk = ss_cdemo_sk
               AND cd_marital_status = 'U'
               AND cd_education_status = 'Advanced Degree'
               AND ss_sales_price BETWEEN 100.00 AND 150.00
               AND hd_dep_count = 3 )
              OR ( ss_hdemo_sk = hd_demo_sk
                   AND cd_demo_sk = ss_cdemo_sk
                   AND cd_marital_status = 'M'
                   AND cd_education_status = 'Primary'
                   AND ss_sales_price BETWEEN 50.00 AND 100.00
                   AND hd_dep_count = 1 )
              OR ( ss_hdemo_sk = hd_demo_sk
                   AND cd_demo_sk = ss_cdemo_sk
                   AND cd_marital_status = 'D'
                   AND cd_education_status = 'Secondary'
                   AND ss_sales_price BETWEEN 150.00 AND 200.00
                   AND hd_dep_count = 1 ) )
       AND ( ( ss_addr_sk = ca_address_sk
               AND ca_country = 'United States'
               AND ca_state IN ( 'AZ', 'NE', 'IA' )
               AND ss_net_profit BETWEEN 100 AND 200 )
              OR ( ss_addr_sk = ca_address_sk
                   AND ca_country = 'United States'
                   AND ca_state IN ( 'MS', 'CA', 'NV' )
                   AND ss_net_profit BETWEEN 150 AND 300 )
              OR ( ss_addr_sk = ca_address_sk
                   AND ca_country = 'United States'
                   AND ca_state IN ( 'GA', 'TX', 'NJ' )
                   AND ss_net_profit BETWEEN 50 AND 250 ) );
SELECT
  AVG("store_sales"."ss_quantity") AS "_col_0",
  AVG("store_sales"."ss_ext_sales_price") AS "_col_1",
  AVG("store_sales"."ss_ext_wholesale_cost") AS "_col_2",
  SUM("store_sales"."ss_ext_wholesale_cost") AS "_col_3"
FROM "store_sales" AS "store_sales"
CROSS JOIN "household_demographics" AS "household_demographics"
JOIN "customer_address" AS "customer_address"
  ON (
    "customer_address"."ca_address_sk" = "store_sales"."ss_addr_sk"
    AND "customer_address"."ca_country" = 'United States'
    AND "customer_address"."ca_state" IN ('AZ', 'NE', 'IA')
    AND "store_sales"."ss_net_profit" <= 200
    AND "store_sales"."ss_net_profit" >= 100
  )
  OR (
    "customer_address"."ca_address_sk" = "store_sales"."ss_addr_sk"
    AND "customer_address"."ca_country" = 'United States'
    AND "customer_address"."ca_state" IN ('GA', 'TX', 'NJ')
    AND "store_sales"."ss_net_profit" <= 250
    AND "store_sales"."ss_net_profit" >= 50
  )
  OR (
    "customer_address"."ca_address_sk" = "store_sales"."ss_addr_sk"
    AND "customer_address"."ca_country" = 'United States'
    AND "customer_address"."ca_state" IN ('MS', 'CA', 'NV')
    AND "store_sales"."ss_net_profit" <= 300
    AND "store_sales"."ss_net_profit" >= 150
  )
JOIN "customer_demographics" AS "customer_demographics"
  ON (
    "customer_demographics"."cd_demo_sk" = "store_sales"."ss_cdemo_sk"
    AND "customer_demographics"."cd_education_status" = 'Advanced Degree'
    AND "customer_demographics"."cd_marital_status" = 'U'
    AND "household_demographics"."hd_demo_sk" = "store_sales"."ss_hdemo_sk"
    AND "household_demographics"."hd_dep_count" = 3
    AND "store_sales"."ss_sales_price" <= 150.00
    AND "store_sales"."ss_sales_price" >= 100.00
  )
  OR (
    "customer_demographics"."cd_demo_sk" = "store_sales"."ss_cdemo_sk"
    AND "customer_demographics"."cd_education_status" = 'Primary'
    AND "customer_demographics"."cd_marital_status" = 'M'
    AND "household_demographics"."hd_demo_sk" = "store_sales"."ss_hdemo_sk"
    AND "household_demographics"."hd_dep_count" = 1
    AND "store_sales"."ss_sales_price" <= 100.00
    AND "store_sales"."ss_sales_price" >= 50.00
  )
  OR (
    "customer_demographics"."cd_demo_sk" = "store_sales"."ss_cdemo_sk"
    AND "customer_demographics"."cd_education_status" = 'Secondary'
    AND "customer_demographics"."cd_marital_status" = 'D'
    AND "household_demographics"."hd_demo_sk" = "store_sales"."ss_hdemo_sk"
    AND "household_demographics"."hd_dep_count" = 1
    AND "store_sales"."ss_sales_price" <= 200.00
    AND "store_sales"."ss_sales_price" >= 150.00
  )
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  AND "date_dim"."d_year" = 2001
JOIN "store" AS "store"
  ON "store"."s_store_sk" = "store_sales"."ss_store_sk";
