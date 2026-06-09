--------------------------------------
-- TPC-DS 99
--------------------------------------
SELECT SUBSTRING(w_warehouse_name, 1, 20) AS "_col_0",
               sm_type,
               cc_name,
               Sum(CASE
                     WHEN ( cs_ship_date_sk - cs_sold_date_sk <= 30 ) THEN 1
                     ELSE 0
                   END) AS "30 days",
               Sum(CASE
                     WHEN ( cs_ship_date_sk - cs_sold_date_sk > 30 )
                          AND ( cs_ship_date_sk - cs_sold_date_sk <= 60 ) THEN 1
                     ELSE 0
                   END) AS "31-60 days",
               Sum(CASE
                     WHEN ( cs_ship_date_sk - cs_sold_date_sk > 60 )
                          AND ( cs_ship_date_sk - cs_sold_date_sk <= 90 ) THEN 1
                     ELSE 0
                   END) AS "61-90 days",
               Sum(CASE
                     WHEN ( cs_ship_date_sk - cs_sold_date_sk > 90 )
                          AND ( cs_ship_date_sk - cs_sold_date_sk <= 120 ) THEN
                     1
                     ELSE 0
                   END) AS "91-120 days",
               Sum(CASE
                     WHEN ( cs_ship_date_sk - cs_sold_date_sk > 120 ) THEN 1
                     ELSE 0
                   END) AS ">120 days"
FROM   catalog_sales,
       warehouse,
       ship_mode,
       call_center,
       date_dim
WHERE  d_month_seq BETWEEN 1200 AND 1200 + 11
       AND cs_ship_date_sk = d_date_sk
       AND cs_warehouse_sk = w_warehouse_sk
       AND cs_ship_mode_sk = sm_ship_mode_sk
       AND cs_call_center_sk = cc_call_center_sk
GROUP  BY SUBSTRING(w_warehouse_name, 1, 20),
          sm_type,
          cc_name
ORDER  BY SUBSTRING(w_warehouse_name, 1, 20),
          sm_type,
          cc_name
LIMIT 100;
SELECT
  SUBSTRING("warehouse"."w_warehouse_name", 1, 20) AS "_col_0",
  "ship_mode"."sm_type" AS "sm_type",
  "call_center"."cc_name" AS "cc_name",
  SUM(
    CASE
      WHEN "catalog_sales"."cs_ship_date_sk" - "catalog_sales"."cs_sold_date_sk" <= 30
      THEN 1
      ELSE 0
    END
  ) AS "30 days",
  SUM(
    CASE
      WHEN "catalog_sales"."cs_ship_date_sk" - "catalog_sales"."cs_sold_date_sk" <= 60
      AND "catalog_sales"."cs_ship_date_sk" - "catalog_sales"."cs_sold_date_sk" > 30
      THEN 1
      ELSE 0
    END
  ) AS "31-60 days",
  SUM(
    CASE
      WHEN "catalog_sales"."cs_ship_date_sk" - "catalog_sales"."cs_sold_date_sk" <= 90
      AND "catalog_sales"."cs_ship_date_sk" - "catalog_sales"."cs_sold_date_sk" > 60
      THEN 1
      ELSE 0
    END
  ) AS "61-90 days",
  SUM(
    CASE
      WHEN "catalog_sales"."cs_ship_date_sk" - "catalog_sales"."cs_sold_date_sk" <= 120
      AND "catalog_sales"."cs_ship_date_sk" - "catalog_sales"."cs_sold_date_sk" > 90
      THEN 1
      ELSE 0
    END
  ) AS "91-120 days",
  SUM(
    CASE
      WHEN "catalog_sales"."cs_ship_date_sk" - "catalog_sales"."cs_sold_date_sk" > 120
      THEN 1
      ELSE 0
    END
  ) AS ">120 days"
FROM "catalog_sales" AS "catalog_sales"
JOIN "call_center" AS "call_center"
  ON "call_center"."cc_call_center_sk" = "catalog_sales"."cs_call_center_sk"
JOIN "date_dim" AS "date_dim"
  ON "catalog_sales"."cs_ship_date_sk" = "date_dim"."d_date_sk"
  AND "date_dim"."d_month_seq" <= 1211
  AND "date_dim"."d_month_seq" >= 1200
JOIN "ship_mode" AS "ship_mode"
  ON "catalog_sales"."cs_ship_mode_sk" = "ship_mode"."sm_ship_mode_sk"
JOIN "warehouse" AS "warehouse"
  ON "catalog_sales"."cs_warehouse_sk" = "warehouse"."w_warehouse_sk"
GROUP BY
  SUBSTRING("warehouse"."w_warehouse_name", 1, 20),
  "ship_mode"."sm_type",
  "call_center"."cc_name"
ORDER BY
  "_col_0",
  "sm_type",
  "cc_name"
LIMIT 100;
