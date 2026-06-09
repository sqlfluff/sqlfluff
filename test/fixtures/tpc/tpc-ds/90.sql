--------------------------------------
-- TPC-DS 90
--------------------------------------
SELECT Cast(amc AS DECIMAL(15, 4)) / Cast(pmc AS DECIMAL(15, 4))
               am_pm_ratio
FROM   (SELECT Count(*) amc
        FROM   web_sales,
               household_demographics,
               time_dim,
               web_page
        WHERE  ws_sold_time_sk = time_dim.t_time_sk
               AND ws_ship_hdemo_sk = household_demographics.hd_demo_sk
               AND ws_web_page_sk = web_page.wp_web_page_sk
               AND time_dim.t_hour BETWEEN 12 AND 12 + 1
               AND household_demographics.hd_dep_count = 8
               AND web_page.wp_char_count BETWEEN 5000 AND 5200) at1,
       (SELECT Count(*) pmc
        FROM   web_sales,
               household_demographics,
               time_dim,
               web_page
        WHERE  ws_sold_time_sk = time_dim.t_time_sk
               AND ws_ship_hdemo_sk = household_demographics.hd_demo_sk
               AND ws_web_page_sk = web_page.wp_web_page_sk
               AND time_dim.t_hour BETWEEN 20 AND 20 + 1
               AND household_demographics.hd_dep_count = 8
               AND web_page.wp_char_count BETWEEN 5000 AND 5200) pt
ORDER  BY am_pm_ratio
LIMIT 100;
WITH "web_sales_2" AS (
  SELECT
    "web_sales"."ws_sold_time_sk" AS "ws_sold_time_sk",
    "web_sales"."ws_ship_hdemo_sk" AS "ws_ship_hdemo_sk",
    "web_sales"."ws_web_page_sk" AS "ws_web_page_sk"
  FROM "web_sales" AS "web_sales"
), "household_demographics_2" AS (
  SELECT
    "household_demographics"."hd_demo_sk" AS "hd_demo_sk",
    "household_demographics"."hd_dep_count" AS "hd_dep_count"
  FROM "household_demographics" AS "household_demographics"
  WHERE
    "household_demographics"."hd_dep_count" = 8
), "web_page_2" AS (
  SELECT
    "web_page"."wp_web_page_sk" AS "wp_web_page_sk",
    "web_page"."wp_char_count" AS "wp_char_count"
  FROM "web_page" AS "web_page"
  WHERE
    "web_page"."wp_char_count" <= 5200 AND "web_page"."wp_char_count" >= 5000
), "at1" AS (
  SELECT
    COUNT(*) AS "amc"
  FROM "web_sales_2" AS "web_sales"
  JOIN "household_demographics_2" AS "household_demographics"
    ON "household_demographics"."hd_demo_sk" = "web_sales"."ws_ship_hdemo_sk"
  JOIN "time_dim" AS "time_dim"
    ON "time_dim"."t_hour" <= 13
    AND "time_dim"."t_hour" >= 12
    AND "time_dim"."t_time_sk" = "web_sales"."ws_sold_time_sk"
  JOIN "web_page_2" AS "web_page"
    ON "web_page"."wp_web_page_sk" = "web_sales"."ws_web_page_sk"
), "pt" AS (
  SELECT
    COUNT(*) AS "pmc"
  FROM "web_sales_2" AS "web_sales"
  JOIN "household_demographics_2" AS "household_demographics"
    ON "household_demographics"."hd_demo_sk" = "web_sales"."ws_ship_hdemo_sk"
  JOIN "time_dim" AS "time_dim"
    ON "time_dim"."t_hour" <= 21
    AND "time_dim"."t_hour" >= 20
    AND "time_dim"."t_time_sk" = "web_sales"."ws_sold_time_sk"
  JOIN "web_page_2" AS "web_page"
    ON "web_page"."wp_web_page_sk" = "web_sales"."ws_web_page_sk"
)
SELECT
  CAST("at1"."amc" AS DECIMAL(15, 4)) / CAST("pt"."pmc" AS DECIMAL(15, 4)) AS "am_pm_ratio"
FROM "at1" AS "at1"
CROSS JOIN "pt" AS "pt"
ORDER BY
  "am_pm_ratio"
LIMIT 100;
