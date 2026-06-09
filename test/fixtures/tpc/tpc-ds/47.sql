--------------------------------------
-- TPC-DS 47
--------------------------------------
WITH v1
     AS (SELECT i_category,
                i_brand,
                s_store_name,
                s_company_name,
                d_year,
                d_moy,
                Sum(ss_sales_price)         sum_sales,
                Avg(Sum(ss_sales_price))
                  OVER (
                    partition BY i_category, i_brand, s_store_name,
                  s_company_name,
                  d_year)
                                            avg_monthly_sales,
                Rank()
                  OVER (
                    partition BY i_category, i_brand, s_store_name,
                  s_company_name
                    ORDER BY d_year, d_moy) rn
         FROM   item,
                store_sales,
                date_dim,
                store
         WHERE  ss_item_sk = i_item_sk
                AND ss_sold_date_sk = d_date_sk
                AND ss_store_sk = s_store_sk
                AND ( d_year = 1999
                       OR ( d_year = 1999 - 1
                            AND d_moy = 12 )
                       OR ( d_year = 1999 + 1
                            AND d_moy = 1 ) )
         GROUP  BY i_category,
                   i_brand,
                   s_store_name,
                   s_company_name,
                   d_year,
                   d_moy),
     v2
     AS (SELECT v1.i_category,
                v1.d_year,
                v1.d_moy,
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
                AND v1.s_store_name = v1_lag.s_store_name
                AND v1.s_store_name = v1_lead.s_store_name
                AND v1.s_company_name = v1_lag.s_company_name
                AND v1.s_company_name = v1_lead.s_company_name
                AND v1.rn = v1_lag.rn + 1
                AND v1.rn = v1_lead.rn - 1)
SELECT *
FROM   v2
WHERE  d_year = 1999
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
    "store"."s_store_name" AS "s_store_name",
    "store"."s_company_name" AS "s_company_name",
    "date_dim"."d_year" AS "d_year",
    "date_dim"."d_moy" AS "d_moy",
    SUM("store_sales"."ss_sales_price") AS "sum_sales",
    AVG(SUM("store_sales"."ss_sales_price")) OVER (
      PARTITION BY "item"."i_category", "item"."i_brand", "store"."s_store_name", "store"."s_company_name", "date_dim"."d_year"
    ) AS "avg_monthly_sales",
    RANK() OVER (
      PARTITION BY "item"."i_category", "item"."i_brand", "store"."s_store_name", "store"."s_company_name"
      ORDER BY "date_dim"."d_year", "date_dim"."d_moy"
    ) AS "rn"
  FROM "item" AS "item"
  JOIN "store_sales" AS "store_sales"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
    AND (
      "date_dim"."d_moy" = 1 OR "date_dim"."d_moy" = 12 OR "date_dim"."d_year" = 1999
    )
    AND (
      "date_dim"."d_moy" = 1 OR "date_dim"."d_year" = 1998 OR "date_dim"."d_year" = 1999
    )
    AND (
      "date_dim"."d_moy" = 12
      OR "date_dim"."d_year" = 1999
      OR "date_dim"."d_year" = 2000
    )
    AND (
      "date_dim"."d_year" = 1998
      OR "date_dim"."d_year" = 1999
      OR "date_dim"."d_year" = 2000
    )
  JOIN "store" AS "store"
    ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
  GROUP BY
    "item"."i_category",
    "item"."i_brand",
    "store"."s_store_name",
    "store"."s_company_name",
    "date_dim"."d_year",
    "date_dim"."d_moy"
)
SELECT
  "v1"."i_category" AS "i_category",
  "v1"."d_year" AS "d_year",
  "v1"."d_moy" AS "d_moy",
  "v1"."avg_monthly_sales" AS "avg_monthly_sales",
  "v1"."sum_sales" AS "sum_sales",
  "v1_lag"."sum_sales" AS "psum",
  "v1_lead"."sum_sales" AS "nsum"
FROM "v1" AS "v1"
JOIN "v1" AS "v1_lag"
  ON "v1"."i_brand" = "v1_lag"."i_brand"
  AND "v1"."i_category" = "v1_lag"."i_category"
  AND "v1"."rn" = "v1_lag"."rn" + 1
  AND "v1"."s_company_name" = "v1_lag"."s_company_name"
  AND "v1"."s_store_name" = "v1_lag"."s_store_name"
JOIN "v1" AS "v1_lead"
  ON "v1"."i_brand" = "v1_lead"."i_brand"
  AND "v1"."i_category" = "v1_lead"."i_category"
  AND "v1"."rn" = "v1_lead"."rn" - 1
  AND "v1"."s_company_name" = "v1_lead"."s_company_name"
  AND "v1"."s_store_name" = "v1_lead"."s_store_name"
WHERE
  "v1"."avg_monthly_sales" > 0
  AND "v1"."d_year" = 1999
  AND CASE
    WHEN "v1"."avg_monthly_sales" > 0
    THEN ABS("v1"."sum_sales" - "v1"."avg_monthly_sales") / "v1"."avg_monthly_sales"
    ELSE NULL
  END > 0.1
ORDER BY
  "v1"."sum_sales" - "v1"."avg_monthly_sales",
  "d_moy"
LIMIT 100;
