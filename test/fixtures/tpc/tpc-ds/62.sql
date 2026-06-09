--------------------------------------
-- TPC-DS 62
--------------------------------------
SELECT SUBSTRING(w_warehouse_name, 1, 20) AS "_col_0",
               sm_type,
               web_name,
               Sum(CASE
                     WHEN ( ws_ship_date_sk - ws_sold_date_sk <= 30 ) THEN 1
                     ELSE 0
                   END) AS "30 days",
               Sum(CASE
                     WHEN ( ws_ship_date_sk - ws_sold_date_sk > 30 )
                          AND ( ws_ship_date_sk - ws_sold_date_sk <= 60 ) THEN 1
                     ELSE 0
                   END) AS "31-60 days",
               Sum(CASE
                     WHEN ( ws_ship_date_sk - ws_sold_date_sk > 60 )
                          AND ( ws_ship_date_sk - ws_sold_date_sk <= 90 ) THEN 1
                     ELSE 0
                   END) AS "61-90 days",
               Sum(CASE
                     WHEN ( ws_ship_date_sk - ws_sold_date_sk > 90 )
                          AND ( ws_ship_date_sk - ws_sold_date_sk <= 120 ) THEN
                     1
                     ELSE 0
                   END) AS "91-120 days",
               Sum(CASE
                     WHEN ( ws_ship_date_sk - ws_sold_date_sk > 120 ) THEN 1
                     ELSE 0
                   END) AS ">120 days"
FROM   web_sales,
       warehouse,
       ship_mode,
       web_site,
       date_dim
WHERE  d_month_seq BETWEEN 1222 AND 1222 + 11
       AND ws_ship_date_sk = d_date_sk
       AND ws_warehouse_sk = w_warehouse_sk
       AND ws_ship_mode_sk = sm_ship_mode_sk
       AND ws_web_site_sk = web_site_sk
GROUP  BY SUBSTRING(w_warehouse_name, 1, 20),
          sm_type,
          web_name
ORDER  BY SUBSTRING(w_warehouse_name, 1, 20),
          sm_type,
          web_name
LIMIT 100;
SELECT
  SUBSTRING("warehouse"."w_warehouse_name", 1, 20) AS "_col_0",
  "ship_mode"."sm_type" AS "sm_type",
  "web_site"."web_name" AS "web_name",
  SUM(
    CASE
      WHEN "web_sales"."ws_ship_date_sk" - "web_sales"."ws_sold_date_sk" <= 30
      THEN 1
      ELSE 0
    END
  ) AS "30 days",
  SUM(
    CASE
      WHEN "web_sales"."ws_ship_date_sk" - "web_sales"."ws_sold_date_sk" <= 60
      AND "web_sales"."ws_ship_date_sk" - "web_sales"."ws_sold_date_sk" > 30
      THEN 1
      ELSE 0
    END
  ) AS "31-60 days",
  SUM(
    CASE
      WHEN "web_sales"."ws_ship_date_sk" - "web_sales"."ws_sold_date_sk" <= 90
      AND "web_sales"."ws_ship_date_sk" - "web_sales"."ws_sold_date_sk" > 60
      THEN 1
      ELSE 0
    END
  ) AS "61-90 days",
  SUM(
    CASE
      WHEN "web_sales"."ws_ship_date_sk" - "web_sales"."ws_sold_date_sk" <= 120
      AND "web_sales"."ws_ship_date_sk" - "web_sales"."ws_sold_date_sk" > 90
      THEN 1
      ELSE 0
    END
  ) AS "91-120 days",
  SUM(
    CASE
      WHEN "web_sales"."ws_ship_date_sk" - "web_sales"."ws_sold_date_sk" > 120
      THEN 1
      ELSE 0
    END
  ) AS ">120 days"
FROM "web_sales" AS "web_sales"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_date_sk" = "web_sales"."ws_ship_date_sk"
  AND "date_dim"."d_month_seq" <= 1233
  AND "date_dim"."d_month_seq" >= 1222
JOIN "ship_mode" AS "ship_mode"
  ON "ship_mode"."sm_ship_mode_sk" = "web_sales"."ws_ship_mode_sk"
JOIN "warehouse" AS "warehouse"
  ON "warehouse"."w_warehouse_sk" = "web_sales"."ws_warehouse_sk"
JOIN "web_site" AS "web_site"
  ON "web_sales"."ws_web_site_sk" = "web_site"."web_site_sk"
GROUP BY
  SUBSTRING("warehouse"."w_warehouse_name", 1, 20),
  "ship_mode"."sm_type",
  "web_site"."web_name"
ORDER BY
  "_col_0",
  "sm_type",
  "web_name"
LIMIT 100;
