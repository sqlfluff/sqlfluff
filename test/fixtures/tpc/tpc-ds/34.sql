--------------------------------------
-- TPC-DS 34
--------------------------------------
SELECT c_last_name,
       c_first_name,
       c_salutation,
       c_preferred_cust_flag,
       ss_ticket_number,
       cnt
FROM   (SELECT ss_ticket_number,
               ss_customer_sk,
               Count(*) cnt
        FROM   store_sales,
               date_dim,
               store,
               household_demographics
        WHERE  store_sales.ss_sold_date_sk = date_dim.d_date_sk
               AND store_sales.ss_store_sk = store.s_store_sk
               AND store_sales.ss_hdemo_sk = household_demographics.hd_demo_sk
               AND ( date_dim.d_dom BETWEEN 1 AND 3
                      OR date_dim.d_dom BETWEEN 25 AND 28 )
               AND ( household_demographics.hd_buy_potential = '>10000'
                      OR household_demographics.hd_buy_potential = 'unknown' )
               AND household_demographics.hd_vehicle_count > 0
               AND ( CASE
                       WHEN household_demographics.hd_vehicle_count > 0 THEN
                       household_demographics.hd_dep_count /
                       household_demographics.hd_vehicle_count
                       ELSE NULL
                     END ) > 1.2
               AND date_dim.d_year IN ( 1999, 1999 + 1, 1999 + 2 )
               AND store.s_county IN ( 'Williamson County', 'Williamson County',
                                       'Williamson County',
                                                             'Williamson County'
                                       ,
                                       'Williamson County', 'Williamson County',
                                           'Williamson County',
                                                             'Williamson County'
                                     )
        GROUP  BY ss_ticket_number,
                  ss_customer_sk) dn,
       customer
WHERE  ss_customer_sk = c_customer_sk
       AND cnt BETWEEN 15 AND 20
ORDER  BY c_last_name,
          c_first_name,
          c_salutation,
          c_preferred_cust_flag DESC;
WITH "dn" AS (
  SELECT
    "store_sales"."ss_ticket_number" AS "ss_ticket_number",
    "store_sales"."ss_customer_sk" AS "ss_customer_sk",
    COUNT(*) AS "cnt"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
    AND "date_dim"."d_year" IN (1999, 2000, 2001)
    AND (
      (
        "date_dim"."d_dom" <= 28 AND "date_dim"."d_dom" >= 25
      )
      OR (
        "date_dim"."d_dom" <= 3 AND "date_dim"."d_dom" >= 1
      )
    )
  JOIN "household_demographics" AS "household_demographics"
    ON (
      "household_demographics"."hd_buy_potential" = '>10000'
      OR "household_demographics"."hd_buy_potential" = 'unknown'
    )
    AND "household_demographics"."hd_demo_sk" = "store_sales"."ss_hdemo_sk"
    AND "household_demographics"."hd_vehicle_count" > 0
    AND CASE
      WHEN "household_demographics"."hd_vehicle_count" > 0
      THEN "household_demographics"."hd_dep_count" / "household_demographics"."hd_vehicle_count"
      ELSE NULL
    END > 1.2
  JOIN "store" AS "store"
    ON "store"."s_county" IN (
      'Williamson County',
      'Williamson County',
      'Williamson County',
      'Williamson County',
      'Williamson County',
      'Williamson County',
      'Williamson County',
      'Williamson County'
    )
    AND "store"."s_store_sk" = "store_sales"."ss_store_sk"
  GROUP BY
    "store_sales"."ss_ticket_number",
    "store_sales"."ss_customer_sk"
)
SELECT
  "customer"."c_last_name" AS "c_last_name",
  "customer"."c_first_name" AS "c_first_name",
  "customer"."c_salutation" AS "c_salutation",
  "customer"."c_preferred_cust_flag" AS "c_preferred_cust_flag",
  "dn"."ss_ticket_number" AS "ss_ticket_number",
  "dn"."cnt" AS "cnt"
FROM "dn" AS "dn"
JOIN "customer" AS "customer"
  ON "customer"."c_customer_sk" = "dn"."ss_customer_sk"
WHERE
  "dn"."cnt" <= 20 AND "dn"."cnt" >= 15
ORDER BY
  "c_last_name",
  "c_first_name",
  "c_salutation",
  "c_preferred_cust_flag" DESC;
