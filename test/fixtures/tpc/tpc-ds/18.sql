--------------------------------------
-- TPC-DS 18
--------------------------------------
SELECT i_item_id,
               ca_country,
               ca_state,
               ca_county,
               Avg(Cast(cs_quantity AS NUMERIC(12, 2)))      agg1,
               Avg(Cast(cs_list_price AS NUMERIC(12, 2)))    agg2,
               Avg(Cast(cs_coupon_amt AS NUMERIC(12, 2)))    agg3,
               Avg(Cast(cs_sales_price AS NUMERIC(12, 2)))   agg4,
               Avg(Cast(cs_net_profit AS NUMERIC(12, 2)))    agg5,
               Avg(Cast(c_birth_year AS NUMERIC(12, 2)))     agg6,
               Avg(Cast(cd1.cd_dep_count AS NUMERIC(12, 2))) agg7
FROM   catalog_sales,
       customer_demographics cd1,
       customer_demographics cd2,
       customer,
       customer_address,
       date_dim,
       item
WHERE  cs_sold_date_sk = d_date_sk
       AND cs_item_sk = i_item_sk
       AND cs_bill_cdemo_sk = cd1.cd_demo_sk
       AND cs_bill_customer_sk = c_customer_sk
       AND cd1.cd_gender = 'F'
       AND cd1.cd_education_status = 'Secondary'
       AND c_current_cdemo_sk = cd2.cd_demo_sk
       AND c_current_addr_sk = ca_address_sk
       AND c_birth_month IN ( 8, 4, 2, 5,
                              11, 9 )
       AND d_year = 2001
       AND ca_state IN ( 'KS', 'IA', 'AL', 'UT',
                         'VA', 'NC', 'TX' )
GROUP  BY rollup ( i_item_id, ca_country, ca_state, ca_county )
ORDER  BY ca_country,
          ca_state,
          ca_county,
          i_item_id
LIMIT 100;
SELECT
  "item"."i_item_id" AS "i_item_id",
  "customer_address"."ca_country" AS "ca_country",
  "customer_address"."ca_state" AS "ca_state",
  "customer_address"."ca_county" AS "ca_county",
  AVG(CAST("catalog_sales"."cs_quantity" AS DECIMAL(12, 2))) AS "agg1",
  AVG(CAST("catalog_sales"."cs_list_price" AS DECIMAL(12, 2))) AS "agg2",
  AVG(CAST("catalog_sales"."cs_coupon_amt" AS DECIMAL(12, 2))) AS "agg3",
  AVG(CAST("catalog_sales"."cs_sales_price" AS DECIMAL(12, 2))) AS "agg4",
  AVG(CAST("catalog_sales"."cs_net_profit" AS DECIMAL(12, 2))) AS "agg5",
  AVG(CAST("customer"."c_birth_year" AS DECIMAL(12, 2))) AS "agg6",
  AVG(CAST("cd1"."cd_dep_count" AS DECIMAL(12, 2))) AS "agg7"
FROM "catalog_sales" AS "catalog_sales"
JOIN "customer_demographics" AS "cd1"
  ON "catalog_sales"."cs_bill_cdemo_sk" = "cd1"."cd_demo_sk"
  AND "cd1"."cd_education_status" = 'Secondary'
  AND "cd1"."cd_gender" = 'F'
JOIN "customer" AS "customer"
  ON "catalog_sales"."cs_bill_customer_sk" = "customer"."c_customer_sk"
  AND "customer"."c_birth_month" IN (8, 4, 2, 5, 11, 9)
JOIN "date_dim" AS "date_dim"
  ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  AND "date_dim"."d_year" = 2001
JOIN "item" AS "item"
  ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
JOIN "customer_demographics" AS "cd2"
  ON "cd2"."cd_demo_sk" = "customer"."c_current_cdemo_sk"
JOIN "customer_address" AS "customer_address"
  ON "customer"."c_current_addr_sk" = "customer_address"."ca_address_sk"
  AND "customer_address"."ca_state" IN ('KS', 'IA', 'AL', 'UT', 'VA', 'NC', 'TX')
GROUP BY
  ROLLUP (
    "item"."i_item_id",
    "customer_address"."ca_country",
    "customer_address"."ca_state",
    "customer_address"."ca_county"
  )
ORDER BY
  "ca_country",
  "ca_state",
  "ca_county",
  "i_item_id"
LIMIT 100;
