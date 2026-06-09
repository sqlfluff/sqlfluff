--------------------------------------
-- TPC-DS 35
--------------------------------------
SELECT ca_state,
               cd_gender,
               cd_marital_status,
               cd_dep_count,
               Count(*) cnt1,
               Stddev_samp(cd_dep_count) AS "_col_5",
               Avg(cd_dep_count) AS "_col_6",
               Max(cd_dep_count) AS "_col_7",
               cd_dep_employed_count,
               Count(*) cnt2,
               Stddev_samp(cd_dep_employed_count) AS "_col_10",
               Avg(cd_dep_employed_count) AS "_col_11",
               Max(cd_dep_employed_count) AS "_col_12",
               cd_dep_college_count,
               Count(*) cnt3,
               Stddev_samp(cd_dep_college_count) AS "_col_15",
               Avg(cd_dep_college_count) AS "_col_16",
               Max(cd_dep_college_count) AS "_col_17"
FROM   customer c,
       customer_address ca,
       customer_demographics
WHERE  c.c_current_addr_sk = ca.ca_address_sk
       AND cd_demo_sk = c.c_current_cdemo_sk
       AND EXISTS (SELECT *
                   FROM   store_sales,
                          date_dim
                   WHERE  c.c_customer_sk = ss_customer_sk
                          AND ss_sold_date_sk = d_date_sk
                          AND d_year = 2001
                          AND d_qoy < 4)
       AND ( EXISTS (SELECT *
                     FROM   web_sales,
                            date_dim
                     WHERE  c.c_customer_sk = ws_bill_customer_sk
                            AND ws_sold_date_sk = d_date_sk
                            AND d_year = 2001
                            AND d_qoy < 4)
              OR EXISTS (SELECT *
                         FROM   catalog_sales,
                                date_dim
                         WHERE  c.c_customer_sk = cs_ship_customer_sk
                                AND cs_sold_date_sk = d_date_sk
                                AND d_year = 2001
                                AND d_qoy < 4) )
GROUP  BY ca_state,
          cd_gender,
          cd_marital_status,
          cd_dep_count,
          cd_dep_employed_count,
          cd_dep_college_count
ORDER  BY ca_state,
          cd_gender,
          cd_marital_status,
          cd_dep_count,
          cd_dep_employed_count,
          cd_dep_college_count
LIMIT 100;
WITH "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_date_id" AS "d_date_id",
    "date_dim"."d_date" AS "d_date",
    "date_dim"."d_month_seq" AS "d_month_seq",
    "date_dim"."d_week_seq" AS "d_week_seq",
    "date_dim"."d_quarter_seq" AS "d_quarter_seq",
    "date_dim"."d_year" AS "d_year",
    "date_dim"."d_dow" AS "d_dow",
    "date_dim"."d_moy" AS "d_moy",
    "date_dim"."d_dom" AS "d_dom",
    "date_dim"."d_qoy" AS "d_qoy",
    "date_dim"."d_fy_year" AS "d_fy_year",
    "date_dim"."d_fy_quarter_seq" AS "d_fy_quarter_seq",
    "date_dim"."d_fy_week_seq" AS "d_fy_week_seq",
    "date_dim"."d_day_name" AS "d_day_name",
    "date_dim"."d_quarter_name" AS "d_quarter_name",
    "date_dim"."d_holiday" AS "d_holiday",
    "date_dim"."d_weekend" AS "d_weekend",
    "date_dim"."d_following_holiday" AS "d_following_holiday",
    "date_dim"."d_first_dom" AS "d_first_dom",
    "date_dim"."d_last_dom" AS "d_last_dom",
    "date_dim"."d_same_day_ly" AS "d_same_day_ly",
    "date_dim"."d_same_day_lq" AS "d_same_day_lq",
    "date_dim"."d_current_day" AS "d_current_day",
    "date_dim"."d_current_week" AS "d_current_week",
    "date_dim"."d_current_month" AS "d_current_month",
    "date_dim"."d_current_quarter" AS "d_current_quarter",
    "date_dim"."d_current_year" AS "d_current_year"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_qoy" < 4 AND "date_dim"."d_year" = 2001
), "_u_0" AS (
  SELECT
    "store_sales"."ss_customer_sk" AS "_u_1"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  GROUP BY
    "store_sales"."ss_customer_sk"
), "_u_2" AS (
  SELECT
    "web_sales"."ws_bill_customer_sk" AS "_u_3"
  FROM "web_sales" AS "web_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  GROUP BY
    "web_sales"."ws_bill_customer_sk"
), "_u_4" AS (
  SELECT
    "catalog_sales"."cs_ship_customer_sk" AS "_u_5"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  GROUP BY
    "catalog_sales"."cs_ship_customer_sk"
)
SELECT
  "ca"."ca_state" AS "ca_state",
  "customer_demographics"."cd_gender" AS "cd_gender",
  "customer_demographics"."cd_marital_status" AS "cd_marital_status",
  "customer_demographics"."cd_dep_count" AS "cd_dep_count",
  COUNT(*) AS "cnt1",
  STDDEV_SAMP("customer_demographics"."cd_dep_count") AS "_col_5",
  AVG("customer_demographics"."cd_dep_count") AS "_col_6",
  MAX("customer_demographics"."cd_dep_count") AS "_col_7",
  "customer_demographics"."cd_dep_employed_count" AS "cd_dep_employed_count",
  COUNT(*) AS "cnt2",
  STDDEV_SAMP("customer_demographics"."cd_dep_employed_count") AS "_col_10",
  AVG("customer_demographics"."cd_dep_employed_count") AS "_col_11",
  MAX("customer_demographics"."cd_dep_employed_count") AS "_col_12",
  "customer_demographics"."cd_dep_college_count" AS "cd_dep_college_count",
  COUNT(*) AS "cnt3",
  STDDEV_SAMP("customer_demographics"."cd_dep_college_count") AS "_col_15",
  AVG("customer_demographics"."cd_dep_college_count") AS "_col_16",
  MAX("customer_demographics"."cd_dep_college_count") AS "_col_17"
FROM "customer" AS "c"
JOIN "customer_address" AS "ca"
  ON "c"."c_current_addr_sk" = "ca"."ca_address_sk"
JOIN "customer_demographics" AS "customer_demographics"
  ON "c"."c_current_cdemo_sk" = "customer_demographics"."cd_demo_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "c"."c_customer_sk"
LEFT JOIN "_u_2" AS "_u_2"
  ON "_u_2"."_u_3" = "c"."c_customer_sk"
LEFT JOIN "_u_4" AS "_u_4"
  ON "_u_4"."_u_5" = "c"."c_customer_sk"
WHERE
  NOT "_u_0"."_u_1" IS NULL
  AND (
    NOT "_u_2"."_u_3" IS NULL OR NOT "_u_4"."_u_5" IS NULL
  )
GROUP BY
  "ca"."ca_state",
  "customer_demographics"."cd_gender",
  "customer_demographics"."cd_marital_status",
  "customer_demographics"."cd_dep_count",
  "customer_demographics"."cd_dep_employed_count",
  "customer_demographics"."cd_dep_college_count"
ORDER BY
  "ca_state",
  "cd_gender",
  "cd_marital_status",
  "cd_dep_count",
  "cd_dep_employed_count",
  "cd_dep_college_count"
LIMIT 100;
