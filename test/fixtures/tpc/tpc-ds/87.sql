--------------------------------------
-- TPC-DS 87
--------------------------------------
select count(*) as "_col_0"
from ((select distinct c_last_name, c_first_name, d_date
       from store_sales, date_dim, customer
       where store_sales.ss_sold_date_sk = date_dim.d_date_sk
         and store_sales.ss_customer_sk = customer.c_customer_sk
         and d_month_seq between 1188 and 1188+11)
       except
      (select distinct c_last_name, c_first_name, d_date
       from catalog_sales, date_dim, customer
       where catalog_sales.cs_sold_date_sk = date_dim.d_date_sk
         and catalog_sales.cs_bill_customer_sk = customer.c_customer_sk
         and d_month_seq between 1188 and 1188+11)
       except
      (select distinct c_last_name, c_first_name, d_date
       from web_sales, date_dim, customer
       where web_sales.ws_sold_date_sk = date_dim.d_date_sk
         and web_sales.ws_bill_customer_sk = customer.c_customer_sk
         and d_month_seq between 1188 and 1188+11)
) cool_cust;
WITH "customer_2" AS (
  SELECT
    "customer"."c_customer_sk" AS "c_customer_sk",
    "customer"."c_first_name" AS "c_first_name",
    "customer"."c_last_name" AS "c_last_name"
  FROM "customer" AS "customer"
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_date" AS "d_date",
    "date_dim"."d_month_seq" AS "d_month_seq"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_month_seq" <= 1199 AND "date_dim"."d_month_seq" >= 1188
), "cool_cust" AS (
  (
    SELECT DISTINCT
      "customer"."c_last_name" AS "c_last_name",
      "customer"."c_first_name" AS "c_first_name",
      "date_dim"."d_date" AS "d_date"
    FROM "store_sales" AS "store_sales"
    JOIN "customer_2" AS "customer"
      ON "customer"."c_customer_sk" = "store_sales"."ss_customer_sk"
    JOIN "date_dim_2" AS "date_dim"
      ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  )
  EXCEPT
  (
    SELECT DISTINCT
      "customer"."c_last_name" AS "c_last_name",
      "customer"."c_first_name" AS "c_first_name",
      "date_dim"."d_date" AS "d_date"
    FROM "catalog_sales" AS "catalog_sales"
    JOIN "customer_2" AS "customer"
      ON "catalog_sales"."cs_bill_customer_sk" = "customer"."c_customer_sk"
    JOIN "date_dim_2" AS "date_dim"
      ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  )
  EXCEPT
  (
    SELECT DISTINCT
      "customer"."c_last_name" AS "c_last_name",
      "customer"."c_first_name" AS "c_first_name",
      "date_dim"."d_date" AS "d_date"
    FROM "web_sales" AS "web_sales"
    JOIN "customer_2" AS "customer"
      ON "customer"."c_customer_sk" = "web_sales"."ws_bill_customer_sk"
    JOIN "date_dim_2" AS "date_dim"
      ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  )
)
SELECT
  COUNT(*) AS "_col_0"
FROM "cool_cust" AS "cool_cust";
