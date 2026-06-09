--------------------------------------
-- TPC-DS 4
--------------------------------------
WITH year_total
     AS (SELECT c_customer_id                       customer_id,
                c_first_name                        customer_first_name,
                c_last_name                         customer_last_name,
                c_preferred_cust_flag               customer_preferred_cust_flag
                ,
                c_birth_country
                customer_birth_country,
                c_login                             customer_login,
                c_email_address                     customer_email_address,
                d_year                              dyear,
                Sum(( ( ss_ext_list_price - ss_ext_wholesale_cost
                        - ss_ext_discount_amt
                      )
                      +
                          ss_ext_sales_price ) / 2) year_total,
                's'                                 sale_type
         FROM   customer,
                store_sales,
                date_dim
         WHERE  c_customer_sk = ss_customer_sk
                AND ss_sold_date_sk = d_date_sk
         GROUP  BY c_customer_id,
                   c_first_name,
                   c_last_name,
                   c_preferred_cust_flag,
                   c_birth_country,
                   c_login,
                   c_email_address,
                   d_year
         UNION ALL
         SELECT c_customer_id                             customer_id,
                c_first_name                              customer_first_name,
                c_last_name                               customer_last_name,
                c_preferred_cust_flag
                customer_preferred_cust_flag,
                c_birth_country                           customer_birth_country
                ,
                c_login
                customer_login,
                c_email_address                           customer_email_address
                ,
                d_year                                    dyear
                ,
                Sum(( ( ( cs_ext_list_price
                          - cs_ext_wholesale_cost
                          - cs_ext_discount_amt
                        ) +
                              cs_ext_sales_price ) / 2 )) year_total,
                'c'                                       sale_type
         FROM   customer,
                catalog_sales,
                date_dim
         WHERE  c_customer_sk = cs_bill_customer_sk
                AND cs_sold_date_sk = d_date_sk
         GROUP  BY c_customer_id,
                   c_first_name,
                   c_last_name,
                   c_preferred_cust_flag,
                   c_birth_country,
                   c_login,
                   c_email_address,
                   d_year
         UNION ALL
         SELECT c_customer_id                             customer_id,
                c_first_name                              customer_first_name,
                c_last_name                               customer_last_name,
                c_preferred_cust_flag
                customer_preferred_cust_flag,
                c_birth_country                           customer_birth_country
                ,
                c_login
                customer_login,
                c_email_address                           customer_email_address
                ,
                d_year                                    dyear
                ,
                Sum(( ( ( ws_ext_list_price
                          - ws_ext_wholesale_cost
                          - ws_ext_discount_amt
                        ) +
                              ws_ext_sales_price ) / 2 )) year_total,
                'w'                                       sale_type
         FROM   customer,
                web_sales,
                date_dim
         WHERE  c_customer_sk = ws_bill_customer_sk
                AND ws_sold_date_sk = d_date_sk
         GROUP  BY c_customer_id,
                   c_first_name,
                   c_last_name,
                   c_preferred_cust_flag,
                   c_birth_country,
                   c_login,
                   c_email_address,
                   d_year)
SELECT t_s_secyear.customer_id,
               t_s_secyear.customer_first_name,
               t_s_secyear.customer_last_name,
               t_s_secyear.customer_preferred_cust_flag
FROM   year_total t_s_firstyear,
       year_total t_s_secyear,
       year_total t_c_firstyear,
       year_total t_c_secyear,
       year_total t_w_firstyear,
       year_total t_w_secyear
WHERE  t_s_secyear.customer_id = t_s_firstyear.customer_id
       AND t_s_firstyear.customer_id = t_c_secyear.customer_id
       AND t_s_firstyear.customer_id = t_c_firstyear.customer_id
       AND t_s_firstyear.customer_id = t_w_firstyear.customer_id
       AND t_s_firstyear.customer_id = t_w_secyear.customer_id
       AND t_s_firstyear.sale_type = 's'
       AND t_c_firstyear.sale_type = 'c'
       AND t_w_firstyear.sale_type = 'w'
       AND t_s_secyear.sale_type = 's'
       AND t_c_secyear.sale_type = 'c'
       AND t_w_secyear.sale_type = 'w'
       AND t_s_firstyear.dyear = 2001
       AND t_s_secyear.dyear = 2001 + 1
       AND t_c_firstyear.dyear = 2001
       AND t_c_secyear.dyear = 2001 + 1
       AND t_w_firstyear.dyear = 2001
       AND t_w_secyear.dyear = 2001 + 1
       AND t_s_firstyear.year_total > 0
       AND t_c_firstyear.year_total > 0
       AND t_w_firstyear.year_total > 0
       AND CASE
             WHEN t_c_firstyear.year_total > 0 THEN t_c_secyear.year_total /
                                                    t_c_firstyear.year_total
             ELSE NULL
           END > CASE
                   WHEN t_s_firstyear.year_total > 0 THEN
                   t_s_secyear.year_total /
                   t_s_firstyear.year_total
                   ELSE NULL
                 END
       AND CASE
             WHEN t_c_firstyear.year_total > 0 THEN t_c_secyear.year_total /
                                                    t_c_firstyear.year_total
             ELSE NULL
           END > CASE
                   WHEN t_w_firstyear.year_total > 0 THEN
                   t_w_secyear.year_total /
                   t_w_firstyear.year_total
                   ELSE NULL
                 END
ORDER  BY t_s_secyear.customer_id,
          t_s_secyear.customer_first_name,
          t_s_secyear.customer_last_name,
          t_s_secyear.customer_preferred_cust_flag
LIMIT 100;
WITH "customer_2" AS (
  SELECT
    "customer"."c_customer_sk" AS "c_customer_sk",
    "customer"."c_customer_id" AS "c_customer_id",
    "customer"."c_first_name" AS "c_first_name",
    "customer"."c_last_name" AS "c_last_name",
    "customer"."c_preferred_cust_flag" AS "c_preferred_cust_flag",
    "customer"."c_birth_country" AS "c_birth_country",
    "customer"."c_login" AS "c_login",
    "customer"."c_email_address" AS "c_email_address"
  FROM "customer" AS "customer"
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year"
  FROM "date_dim" AS "date_dim"
), "year_total" AS (
  SELECT
    "customer"."c_customer_id" AS "customer_id",
    "customer"."c_first_name" AS "customer_first_name",
    "customer"."c_last_name" AS "customer_last_name",
    "customer"."c_preferred_cust_flag" AS "customer_preferred_cust_flag",
    "date_dim"."d_year" AS "dyear",
    SUM(
      (
        (
          "store_sales"."ss_ext_list_price" - "store_sales"."ss_ext_wholesale_cost" - "store_sales"."ss_ext_discount_amt"
        ) + "store_sales"."ss_ext_sales_price"
      ) / 2
    ) AS "year_total",
    's' AS "sale_type"
  FROM "customer_2" AS "customer"
  JOIN "store_sales" AS "store_sales"
    ON "customer"."c_customer_sk" = "store_sales"."ss_customer_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  GROUP BY
    "customer"."c_customer_id",
    "customer"."c_first_name",
    "customer"."c_last_name",
    "customer"."c_preferred_cust_flag",
    "customer"."c_birth_country",
    "customer"."c_login",
    "customer"."c_email_address",
    "date_dim"."d_year"
  UNION ALL
  SELECT
    "customer"."c_customer_id" AS "customer_id",
    "customer"."c_first_name" AS "customer_first_name",
    "customer"."c_last_name" AS "customer_last_name",
    "customer"."c_preferred_cust_flag" AS "customer_preferred_cust_flag",
    "date_dim"."d_year" AS "dyear",
    SUM(
      (
        (
          (
            "catalog_sales"."cs_ext_list_price" - "catalog_sales"."cs_ext_wholesale_cost" - "catalog_sales"."cs_ext_discount_amt"
          ) + "catalog_sales"."cs_ext_sales_price"
        ) / 2
      )
    ) AS "year_total",
    'c' AS "sale_type"
  FROM "customer_2" AS "customer"
  JOIN "catalog_sales" AS "catalog_sales"
    ON "catalog_sales"."cs_bill_customer_sk" = "customer"."c_customer_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  GROUP BY
    "customer"."c_customer_id",
    "customer"."c_first_name",
    "customer"."c_last_name",
    "customer"."c_preferred_cust_flag",
    "customer"."c_birth_country",
    "customer"."c_login",
    "customer"."c_email_address",
    "date_dim"."d_year"
  UNION ALL
  SELECT
    "customer"."c_customer_id" AS "customer_id",
    "customer"."c_first_name" AS "customer_first_name",
    "customer"."c_last_name" AS "customer_last_name",
    "customer"."c_preferred_cust_flag" AS "customer_preferred_cust_flag",
    "date_dim"."d_year" AS "dyear",
    SUM(
      (
        (
          (
            "web_sales"."ws_ext_list_price" - "web_sales"."ws_ext_wholesale_cost" - "web_sales"."ws_ext_discount_amt"
          ) + "web_sales"."ws_ext_sales_price"
        ) / 2
      )
    ) AS "year_total",
    'w' AS "sale_type"
  FROM "customer_2" AS "customer"
  JOIN "web_sales" AS "web_sales"
    ON "customer"."c_customer_sk" = "web_sales"."ws_bill_customer_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  GROUP BY
    "customer"."c_customer_id",
    "customer"."c_first_name",
    "customer"."c_last_name",
    "customer"."c_preferred_cust_flag",
    "customer"."c_birth_country",
    "customer"."c_login",
    "customer"."c_email_address",
    "date_dim"."d_year"
)
SELECT
  "t_s_secyear"."customer_id" AS "customer_id",
  "t_s_secyear"."customer_first_name" AS "customer_first_name",
  "t_s_secyear"."customer_last_name" AS "customer_last_name",
  "t_s_secyear"."customer_preferred_cust_flag" AS "customer_preferred_cust_flag"
FROM "year_total" AS "t_s_firstyear"
JOIN "year_total" AS "t_c_firstyear"
  ON "t_c_firstyear"."customer_id" = "t_s_firstyear"."customer_id"
  AND "t_c_firstyear"."dyear" = 2001
  AND "t_c_firstyear"."sale_type" = 'c'
  AND "t_c_firstyear"."year_total" > 0
JOIN "year_total" AS "t_s_secyear"
  ON "t_s_firstyear"."customer_id" = "t_s_secyear"."customer_id"
  AND "t_s_secyear"."dyear" = 2002
  AND "t_s_secyear"."sale_type" = 's'
JOIN "year_total" AS "t_w_firstyear"
  ON "t_s_firstyear"."customer_id" = "t_w_firstyear"."customer_id"
  AND "t_w_firstyear"."dyear" = 2001
  AND "t_w_firstyear"."sale_type" = 'w'
  AND "t_w_firstyear"."year_total" > 0
JOIN "year_total" AS "t_c_secyear"
  ON "t_c_secyear"."customer_id" = "t_s_firstyear"."customer_id"
  AND "t_c_secyear"."dyear" = 2002
  AND "t_c_secyear"."sale_type" = 'c'
  AND CASE
    WHEN "t_c_firstyear"."year_total" > 0
    THEN "t_c_secyear"."year_total" / "t_c_firstyear"."year_total"
    ELSE NULL
  END > CASE
    WHEN "t_s_firstyear"."year_total" > 0
    THEN "t_s_secyear"."year_total" / "t_s_firstyear"."year_total"
    ELSE NULL
  END
JOIN "year_total" AS "t_w_secyear"
  ON "t_s_firstyear"."customer_id" = "t_w_secyear"."customer_id"
  AND "t_w_secyear"."dyear" = 2002
  AND "t_w_secyear"."sale_type" = 'w'
  AND CASE
    WHEN "t_c_firstyear"."year_total" > 0
    THEN "t_c_secyear"."year_total" / "t_c_firstyear"."year_total"
    ELSE NULL
  END > CASE
    WHEN "t_w_firstyear"."year_total" > 0
    THEN "t_w_secyear"."year_total" / "t_w_firstyear"."year_total"
    ELSE NULL
  END
WHERE
  "t_s_firstyear"."dyear" = 2001
  AND "t_s_firstyear"."sale_type" = 's'
  AND "t_s_firstyear"."year_total" > 0
ORDER BY
  "t_s_secyear"."customer_id",
  "t_s_secyear"."customer_first_name",
  "t_s_secyear"."customer_last_name",
  "t_s_secyear"."customer_preferred_cust_flag"
LIMIT 100;
