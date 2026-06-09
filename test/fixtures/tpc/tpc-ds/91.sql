--------------------------------------
-- TPC-DS 91
--------------------------------------
SELECT cc_call_center_id call_center,
       cc_name           call_center_name,
       cc_manager        manager,
       Sum(cr_net_loss)  returns_loss
FROM   call_center,
       catalog_returns,
       date_dim,
       customer,
       customer_address,
       customer_demographics,
       household_demographics
WHERE  cr_call_center_sk = cc_call_center_sk
       AND cr_returned_date_sk = d_date_sk
       AND cr_returning_customer_sk = c_customer_sk
       AND cd_demo_sk = c_current_cdemo_sk
       AND hd_demo_sk = c_current_hdemo_sk
       AND ca_address_sk = c_current_addr_sk
       AND d_year = 1999
       AND d_moy = 12
       AND ( ( cd_marital_status = 'M'
               AND cd_education_status = 'Unknown' )
              OR ( cd_marital_status = 'W'
                   AND cd_education_status = 'Advanced Degree' ) )
       AND hd_buy_potential LIKE 'Unknown%'
       AND ca_gmt_offset = -7
GROUP  BY cc_call_center_id,
          cc_name,
          cc_manager,
          cd_marital_status,
          cd_education_status
ORDER  BY Sum(cr_net_loss) DESC;
SELECT
  "call_center"."cc_call_center_id" AS "call_center",
  "call_center"."cc_name" AS "call_center_name",
  "call_center"."cc_manager" AS "manager",
  SUM("catalog_returns"."cr_net_loss") AS "returns_loss"
FROM "call_center" AS "call_center"
JOIN "catalog_returns" AS "catalog_returns"
  ON "call_center"."cc_call_center_sk" = "catalog_returns"."cr_call_center_sk"
JOIN "customer" AS "customer"
  ON "catalog_returns"."cr_returning_customer_sk" = "customer"."c_customer_sk"
JOIN "date_dim" AS "date_dim"
  ON "catalog_returns"."cr_returned_date_sk" = "date_dim"."d_date_sk"
  AND "date_dim"."d_moy" = 12
  AND "date_dim"."d_year" = 1999
JOIN "customer_address" AS "customer_address"
  ON "customer"."c_current_addr_sk" = "customer_address"."ca_address_sk"
  AND "customer_address"."ca_gmt_offset" = -7
JOIN "customer_demographics" AS "customer_demographics"
  ON "customer"."c_current_cdemo_sk" = "customer_demographics"."cd_demo_sk"
  AND (
    "customer_demographics"."cd_education_status" = 'Advanced Degree'
    OR "customer_demographics"."cd_education_status" = 'Unknown'
  )
  AND (
    "customer_demographics"."cd_education_status" = 'Advanced Degree'
    OR "customer_demographics"."cd_marital_status" = 'M'
  )
  AND (
    "customer_demographics"."cd_education_status" = 'Unknown'
    OR "customer_demographics"."cd_marital_status" = 'W'
  )
  AND (
    "customer_demographics"."cd_marital_status" = 'M'
    OR "customer_demographics"."cd_marital_status" = 'W'
  )
JOIN "household_demographics" AS "household_demographics"
  ON "customer"."c_current_hdemo_sk" = "household_demographics"."hd_demo_sk"
  AND "household_demographics"."hd_buy_potential" LIKE 'Unknown%'
GROUP BY
  "call_center"."cc_call_center_id",
  "call_center"."cc_name",
  "call_center"."cc_manager",
  "customer_demographics"."cd_marital_status",
  "customer_demographics"."cd_education_status"
ORDER BY
  "returns_loss" DESC;
