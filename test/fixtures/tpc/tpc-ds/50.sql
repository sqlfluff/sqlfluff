--------------------------------------
-- TPC-DS 50
--------------------------------------
SELECT s_store_name,
               s_company_id,
               s_street_number,
               s_street_name,
               s_street_type,
               s_suite_number,
               s_city,
               s_county,
               s_state,
               s_zip,
               Sum(CASE
                     WHEN ( sr_returned_date_sk - ss_sold_date_sk <= 30 ) THEN 1
                     ELSE 0
                   END) AS "30 days",
               Sum(CASE
                     WHEN ( sr_returned_date_sk - ss_sold_date_sk > 30 )
                          AND ( sr_returned_date_sk - ss_sold_date_sk <= 60 )
                   THEN 1
                     ELSE 0
                   END) AS "31-60 days",
               Sum(CASE
                     WHEN ( sr_returned_date_sk - ss_sold_date_sk > 60 )
                          AND ( sr_returned_date_sk - ss_sold_date_sk <= 90 )
                   THEN 1
                     ELSE 0
                   END) AS "61-90 days",
               Sum(CASE
                     WHEN ( sr_returned_date_sk - ss_sold_date_sk > 90 )
                          AND ( sr_returned_date_sk - ss_sold_date_sk <= 120 )
                   THEN 1
                     ELSE 0
                   END) AS "91-120 days",
               Sum(CASE
                     WHEN ( sr_returned_date_sk - ss_sold_date_sk > 120 ) THEN 1
                     ELSE 0
                   END) AS ">120 days"
FROM   store_sales,
       store_returns,
       store,
       date_dim d1,
       date_dim d2
WHERE  d2.d_year = 2002
       AND d2.d_moy = 9
       AND ss_ticket_number = sr_ticket_number
       AND ss_item_sk = sr_item_sk
       AND ss_sold_date_sk = d1.d_date_sk
       AND sr_returned_date_sk = d2.d_date_sk
       AND ss_customer_sk = sr_customer_sk
       AND ss_store_sk = s_store_sk
GROUP  BY s_store_name,
          s_company_id,
          s_street_number,
          s_street_name,
          s_street_type,
          s_suite_number,
          s_city,
          s_county,
          s_state,
          s_zip
ORDER  BY s_store_name,
          s_company_id,
          s_street_number,
          s_street_name,
          s_street_type,
          s_suite_number,
          s_city,
          s_county,
          s_state,
          s_zip
LIMIT 100;
SELECT
  "store"."s_store_name" AS "s_store_name",
  "store"."s_company_id" AS "s_company_id",
  "store"."s_street_number" AS "s_street_number",
  "store"."s_street_name" AS "s_street_name",
  "store"."s_street_type" AS "s_street_type",
  "store"."s_suite_number" AS "s_suite_number",
  "store"."s_city" AS "s_city",
  "store"."s_county" AS "s_county",
  "store"."s_state" AS "s_state",
  "store"."s_zip" AS "s_zip",
  SUM(
    CASE
      WHEN "store_returns"."sr_returned_date_sk" - "store_sales"."ss_sold_date_sk" <= 30
      THEN 1
      ELSE 0
    END
  ) AS "30 days",
  SUM(
    CASE
      WHEN "store_returns"."sr_returned_date_sk" - "store_sales"."ss_sold_date_sk" <= 60
      AND "store_returns"."sr_returned_date_sk" - "store_sales"."ss_sold_date_sk" > 30
      THEN 1
      ELSE 0
    END
  ) AS "31-60 days",
  SUM(
    CASE
      WHEN "store_returns"."sr_returned_date_sk" - "store_sales"."ss_sold_date_sk" <= 90
      AND "store_returns"."sr_returned_date_sk" - "store_sales"."ss_sold_date_sk" > 60
      THEN 1
      ELSE 0
    END
  ) AS "61-90 days",
  SUM(
    CASE
      WHEN "store_returns"."sr_returned_date_sk" - "store_sales"."ss_sold_date_sk" <= 120
      AND "store_returns"."sr_returned_date_sk" - "store_sales"."ss_sold_date_sk" > 90
      THEN 1
      ELSE 0
    END
  ) AS "91-120 days",
  SUM(
    CASE
      WHEN "store_returns"."sr_returned_date_sk" - "store_sales"."ss_sold_date_sk" > 120
      THEN 1
      ELSE 0
    END
  ) AS ">120 days"
FROM "store_sales" AS "store_sales"
JOIN "date_dim" AS "d1"
  ON "d1"."d_date_sk" = "store_sales"."ss_sold_date_sk"
JOIN "store" AS "store"
  ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
JOIN "store_returns" AS "store_returns"
  ON "store_returns"."sr_customer_sk" = "store_sales"."ss_customer_sk"
  AND "store_returns"."sr_item_sk" = "store_sales"."ss_item_sk"
  AND "store_returns"."sr_ticket_number" = "store_sales"."ss_ticket_number"
JOIN "date_dim" AS "d2"
  ON "d2"."d_date_sk" = "store_returns"."sr_returned_date_sk"
  AND "d2"."d_moy" = 9
  AND "d2"."d_year" = 2002
GROUP BY
  "store"."s_store_name",
  "store"."s_company_id",
  "store"."s_street_number",
  "store"."s_street_name",
  "store"."s_street_type",
  "store"."s_suite_number",
  "store"."s_city",
  "store"."s_county",
  "store"."s_state",
  "store"."s_zip"
ORDER BY
  "s_store_name",
  "s_company_id",
  "s_street_number",
  "s_street_name",
  "s_street_type",
  "s_suite_number",
  "s_city",
  "s_county",
  "s_state",
  "s_zip"
LIMIT 100;
