--------------------------------------
-- TPC-DS 57
--------------------------------------
WITH v1
     AS (SELECT i_category,
                i_brand,
                cc_name,
                d_year,
                d_moy,
                Sum(cs_sales_price)                                    sum_sales
                ,
                Avg(Sum(cs_sales_price))
                  OVER (
                    partition BY i_category, i_brand, cc_name, d_year)
                avg_monthly_sales
                   ,
                Rank()
                  OVER (
                    partition BY i_category, i_brand, cc_name
                    ORDER BY d_year, d_moy)                            rn
         FROM   item,
                catalog_sales,
                date_dim,
                call_center
         WHERE  cs_item_sk = i_item_sk
                AND cs_sold_date_sk = d_date_sk
                AND cc_call_center_sk = cs_call_center_sk
                AND ( d_year = 2000
                       OR ( d_year = 2000 - 1
                            AND d_moy = 12 )
                       OR ( d_year = 2000 + 1
                            AND d_moy = 1 ) )
         GROUP  BY i_category,
                   i_brand,
                   cc_name,
                   d_year,
                   d_moy),
     v2
     AS (SELECT v1.i_brand,
                v1.d_year,
                v1.avg_monthly_sales,
                v1.sum_sales,
                v1_lag.sum_sales  psum,
                v1_lead.sum_sales nsum
         FROM   v1,
                v1 v1_lag,
                v1 v1_lead
         WHERE  v1.i_category = v1_lag.i_category
                AND v1.i_category = v1_lead.i_category
                AND v1.i_brand = v1_lag.i_brand
                AND v1.i_brand = v1_lead.i_brand
                AND v1. cc_name = v1_lag. cc_name
                AND v1. cc_name = v1_lead. cc_name
                AND v1.rn = v1_lag.rn + 1
                AND v1.rn = v1_lead.rn - 1)
SELECT *
FROM   v2
WHERE  d_year = 2000
       AND avg_monthly_sales > 0
       AND CASE
             WHEN avg_monthly_sales > 0 THEN Abs(sum_sales - avg_monthly_sales)
                                             /
                                             avg_monthly_sales
             ELSE NULL
           END > 0.1
ORDER  BY sum_sales - avg_monthly_sales,
          3
LIMIT 100;
WITH "v1" AS (
  SELECT
    "item"."i_category" AS "i_category",
    "item"."i_brand" AS "i_brand",
    "call_center"."cc_name" AS "cc_name",
    "date_dim"."d_year" AS "d_year",
    SUM("catalog_sales"."cs_sales_price") AS "sum_sales",
    AVG(SUM("catalog_sales"."cs_sales_price")) OVER (
      PARTITION BY "item"."i_category", "item"."i_brand", "call_center"."cc_name", "date_dim"."d_year"
    ) AS "avg_monthly_sales",
    RANK() OVER (
      PARTITION BY "item"."i_category", "item"."i_brand", "call_center"."cc_name"
      ORDER BY "date_dim"."d_year", "date_dim"."d_moy"
    ) AS "rn"
  FROM "item" AS "item"
  JOIN "catalog_sales" AS "catalog_sales"
    ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
  JOIN "call_center" AS "call_center"
    ON "call_center"."cc_call_center_sk" = "catalog_sales"."cs_call_center_sk"
  JOIN "date_dim" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
    AND (
      "date_dim"."d_moy" = 1 OR "date_dim"."d_moy" = 12 OR "date_dim"."d_year" = 2000
    )
    AND (
      "date_dim"."d_moy" = 1 OR "date_dim"."d_year" = 1999 OR "date_dim"."d_year" = 2000
    )
    AND (
      "date_dim"."d_moy" = 12
      OR "date_dim"."d_year" = 2000
      OR "date_dim"."d_year" = 2001
    )
    AND (
      "date_dim"."d_year" = 1999
      OR "date_dim"."d_year" = 2000
      OR "date_dim"."d_year" = 2001
    )
  GROUP BY
    "item"."i_category",
    "item"."i_brand",
    "call_center"."cc_name",
    "date_dim"."d_year",
    "date_dim"."d_moy"
)
SELECT
  "v1"."i_brand" AS "i_brand",
  "v1"."d_year" AS "d_year",
  "v1"."avg_monthly_sales" AS "avg_monthly_sales",
  "v1"."sum_sales" AS "sum_sales",
  "v1_lag"."sum_sales" AS "psum",
  "v1_lead"."sum_sales" AS "nsum"
FROM "v1" AS "v1"
JOIN "v1" AS "v1_lag"
  ON "v1"."cc_name" = "v1_lag"."cc_name"
  AND "v1"."i_brand" = "v1_lag"."i_brand"
  AND "v1"."i_category" = "v1_lag"."i_category"
  AND "v1"."rn" = "v1_lag"."rn" + 1
JOIN "v1" AS "v1_lead"
  ON "v1"."cc_name" = "v1_lead"."cc_name"
  AND "v1"."i_brand" = "v1_lead"."i_brand"
  AND "v1"."i_category" = "v1_lead"."i_category"
  AND "v1"."rn" = "v1_lead"."rn" - 1
WHERE
  "v1"."avg_monthly_sales" > 0
  AND "v1"."d_year" = 2000
  AND CASE
    WHEN "v1"."avg_monthly_sales" > 0
    THEN ABS("v1"."sum_sales" - "v1"."avg_monthly_sales") / "v1"."avg_monthly_sales"
    ELSE NULL
  END > 0.1
ORDER BY
  "v1"."sum_sales" - "v1"."avg_monthly_sales",
  "avg_monthly_sales"
LIMIT 100;
