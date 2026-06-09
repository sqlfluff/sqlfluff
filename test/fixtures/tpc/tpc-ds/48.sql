--------------------------------------
-- TPC-DS 48
--------------------------------------
SELECT Sum (ss_quantity) AS "_col_0"
FROM   store_sales,
       store,
       customer_demographics,
       customer_address,
       date_dim
WHERE  s_store_sk = ss_store_sk
       AND ss_sold_date_sk = d_date_sk
       AND d_year = 1999
       AND ( ( cd_demo_sk = ss_cdemo_sk
               AND cd_marital_status = 'W'
               AND cd_education_status = 'Secondary'
               AND ss_sales_price BETWEEN 100.00 AND 150.00 )
              OR ( cd_demo_sk = ss_cdemo_sk
                   AND cd_marital_status = 'M'
                   AND cd_education_status = 'Advanced Degree'
                   AND ss_sales_price BETWEEN 50.00 AND 100.00 )
              OR ( cd_demo_sk = ss_cdemo_sk
                   AND cd_marital_status = 'D'
                   AND cd_education_status = '2 yr Degree'
                   AND ss_sales_price BETWEEN 150.00 AND 200.00 ) )
       AND ( ( ss_addr_sk = ca_address_sk
               AND ca_country = 'United States'
               AND ca_state IN ( 'TX', 'NE', 'MO' )
               AND ss_net_profit BETWEEN 0 AND 2000 )
              OR ( ss_addr_sk = ca_address_sk
                   AND ca_country = 'United States'
                   AND ca_state IN ( 'CO', 'TN', 'ND' )
                   AND ss_net_profit BETWEEN 150 AND 3000 )
              OR ( ss_addr_sk = ca_address_sk
                   AND ca_country = 'United States'
                   AND ca_state IN ( 'OK', 'PA', 'CA' )
                   AND ss_net_profit BETWEEN 50 AND 25000 ) );
SELECT
  SUM("store_sales"."ss_quantity") AS "_col_0"
FROM "store_sales" AS "store_sales"
JOIN "customer_address" AS "customer_address"
  ON (
    "customer_address"."ca_address_sk" = "store_sales"."ss_addr_sk"
    AND "customer_address"."ca_country" = 'United States'
    AND "customer_address"."ca_state" IN ('CO', 'TN', 'ND')
    AND "store_sales"."ss_net_profit" <= 3000
    AND "store_sales"."ss_net_profit" >= 150
  )
  OR (
    "customer_address"."ca_address_sk" = "store_sales"."ss_addr_sk"
    AND "customer_address"."ca_country" = 'United States'
    AND "customer_address"."ca_state" IN ('OK', 'PA', 'CA')
    AND "store_sales"."ss_net_profit" <= 25000
    AND "store_sales"."ss_net_profit" >= 50
  )
  OR (
    "customer_address"."ca_address_sk" = "store_sales"."ss_addr_sk"
    AND "customer_address"."ca_country" = 'United States'
    AND "customer_address"."ca_state" IN ('TX', 'NE', 'MO')
    AND "store_sales"."ss_net_profit" <= 2000
    AND "store_sales"."ss_net_profit" >= 0
  )
JOIN "customer_demographics" AS "customer_demographics"
  ON (
    "customer_demographics"."cd_demo_sk" = "store_sales"."ss_cdemo_sk"
    AND "customer_demographics"."cd_education_status" = '2 yr Degree'
    AND "customer_demographics"."cd_marital_status" = 'D'
    AND "store_sales"."ss_sales_price" <= 200.00
    AND "store_sales"."ss_sales_price" >= 150.00
  )
  OR (
    "customer_demographics"."cd_demo_sk" = "store_sales"."ss_cdemo_sk"
    AND "customer_demographics"."cd_education_status" = 'Advanced Degree'
    AND "customer_demographics"."cd_marital_status" = 'M'
    AND "store_sales"."ss_sales_price" <= 100.00
    AND "store_sales"."ss_sales_price" >= 50.00
  )
  OR (
    "customer_demographics"."cd_demo_sk" = "store_sales"."ss_cdemo_sk"
    AND "customer_demographics"."cd_education_status" = 'Secondary'
    AND "customer_demographics"."cd_marital_status" = 'W'
    AND "store_sales"."ss_sales_price" <= 150.00
    AND "store_sales"."ss_sales_price" >= 100.00
  )
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  AND "date_dim"."d_year" = 1999
JOIN "store" AS "store"
  ON "store"."s_store_sk" = "store_sales"."ss_store_sk";
