--------------------------------------
-- TPC-DS 30
--------------------------------------
WITH customer_total_return
     AS (SELECT wr_returning_customer_sk AS ctr_customer_sk,
                ca_state                 AS ctr_state,
                Sum(wr_return_amt)       AS ctr_total_return
         FROM   web_returns,
                date_dim,
                customer_address
         WHERE  wr_returned_date_sk = d_date_sk
                AND d_year = 2000
                AND wr_returning_addr_sk = ca_address_sk
         GROUP  BY wr_returning_customer_sk,
                   ca_state)
SELECT c_customer_id,
               c_salutation,
               c_first_name,
               c_last_name,
               c_preferred_cust_flag,
               c_birth_day,
               c_birth_month,
               c_birth_year,
               c_birth_country,
               c_login,
               c_email_address,
               c_last_review_date,
               ctr_total_return
FROM   customer_total_return ctr1,
       customer_address,
       customer
WHERE  ctr1.ctr_total_return > (SELECT Avg(ctr_total_return) * 1.2
                                FROM   customer_total_return ctr2
                                WHERE  ctr1.ctr_state = ctr2.ctr_state)
       AND ca_address_sk = c_current_addr_sk
       AND ca_state = 'IN'
       AND ctr1.ctr_customer_sk = c_customer_sk
ORDER  BY c_customer_id,
          c_salutation,
          c_first_name,
          c_last_name,
          c_preferred_cust_flag,
          c_birth_day,
          c_birth_month,
          c_birth_year,
          c_birth_country,
          c_login,
          c_email_address,
          c_last_review_date,
          ctr_total_return
LIMIT 100;
WITH "customer_total_return" AS (
  SELECT
    "web_returns"."wr_returning_customer_sk" AS "ctr_customer_sk",
    "customer_address"."ca_state" AS "ctr_state",
    SUM("web_returns"."wr_return_amt") AS "ctr_total_return"
  FROM "web_returns" AS "web_returns"
  JOIN "customer_address" AS "customer_address"
    ON "customer_address"."ca_address_sk" = "web_returns"."wr_returning_addr_sk"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_returns"."wr_returned_date_sk"
    AND "date_dim"."d_year" = 2000
  GROUP BY
    "web_returns"."wr_returning_customer_sk",
    "customer_address"."ca_state"
), "_u_0" AS (
  SELECT
    AVG("ctr2"."ctr_total_return") * 1.2 AS "_col_0",
    "ctr2"."ctr_state" AS "_u_1"
  FROM "customer_total_return" AS "ctr2"
  GROUP BY
    "ctr2"."ctr_state"
)
SELECT
  "customer"."c_customer_id" AS "c_customer_id",
  "customer"."c_salutation" AS "c_salutation",
  "customer"."c_first_name" AS "c_first_name",
  "customer"."c_last_name" AS "c_last_name",
  "customer"."c_preferred_cust_flag" AS "c_preferred_cust_flag",
  "customer"."c_birth_day" AS "c_birth_day",
  "customer"."c_birth_month" AS "c_birth_month",
  "customer"."c_birth_year" AS "c_birth_year",
  "customer"."c_birth_country" AS "c_birth_country",
  "customer"."c_login" AS "c_login",
  "customer"."c_email_address" AS "c_email_address",
  "customer"."c_last_review_date" AS "c_last_review_date",
  "ctr1"."ctr_total_return" AS "ctr_total_return"
FROM "customer_total_return" AS "ctr1"
JOIN "customer_address" AS "customer_address"
  ON "customer_address"."ca_state" = 'IN'
JOIN "customer" AS "customer"
  ON "ctr1"."ctr_customer_sk" = "customer"."c_customer_sk"
  AND "customer"."c_current_addr_sk" = "customer_address"."ca_address_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "ctr1"."ctr_state"
WHERE
  "_u_0"."_col_0" < "ctr1"."ctr_total_return"
ORDER BY
  "c_customer_id",
  "c_salutation",
  "c_first_name",
  "c_last_name",
  "c_preferred_cust_flag",
  "c_birth_day",
  "c_birth_month",
  "c_birth_year",
  "c_birth_country",
  "c_login",
  "c_email_address",
  "c_last_review_date",
  "ctr_total_return"
LIMIT 100;
