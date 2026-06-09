--------------------------------------
-- TPC-DS 63
--------------------------------------
SELECT *
FROM   (SELECT i_manager_id,
               Sum(ss_sales_price)            sum_sales,
               Avg(Sum(ss_sales_price))
                 OVER (
                   partition BY i_manager_id) avg_monthly_sales
        FROM   item,
               store_sales,
               date_dim,
               store
        WHERE  ss_item_sk = i_item_sk
               AND ss_sold_date_sk = d_date_sk
               AND ss_store_sk = s_store_sk
               AND d_month_seq IN ( 1200, 1200 + 1, 1200 + 2, 1200 + 3,
                                    1200 + 4, 1200 + 5, 1200 + 6, 1200 + 7,
                                    1200 + 8, 1200 + 9, 1200 + 10, 1200 + 11 )
               AND ( ( i_category IN ( 'Books', 'Children', 'Electronics' )
                       AND i_class IN ( 'personal', 'portable', 'reference',
                                        'self-help' )
                       AND i_brand IN ( 'scholaramalgamalg #14',
                                        'scholaramalgamalg #7'
                                        ,
                                        'exportiunivamalg #9',
                                                       'scholaramalgamalg #9' )
                     )
                      OR ( i_category IN ( 'Women', 'Music', 'Men' )
                           AND i_class IN ( 'accessories', 'classical',
                                            'fragrances',
                                            'pants' )
                           AND i_brand IN ( 'amalgimporto #1',
                                            'edu packscholar #1',
                                            'exportiimporto #1',
                                                'importoamalg #1' ) ) )
        GROUP  BY i_manager_id,
                  d_moy) tmp1
WHERE  CASE
         WHEN avg_monthly_sales > 0 THEN Abs (sum_sales - avg_monthly_sales) /
                                         avg_monthly_sales
         ELSE NULL
       END > 0.1
ORDER  BY i_manager_id,
          avg_monthly_sales,
          sum_sales
LIMIT 100;
WITH "tmp1" AS (
  SELECT
    "item"."i_manager_id" AS "i_manager_id",
    SUM("store_sales"."ss_sales_price") AS "sum_sales",
    AVG(SUM("store_sales"."ss_sales_price")) OVER (PARTITION BY "item"."i_manager_id") AS "avg_monthly_sales"
  FROM "item" AS "item"
  JOIN "store_sales" AS "store_sales"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
    AND "date_dim"."d_month_seq" IN (1200, 1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1210, 1211)
  JOIN "store" AS "store"
    ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
  WHERE
    (
      "item"."i_brand" IN ('amalgimporto #1', 'edu packscholar #1', 'exportiimporto #1', 'importoamalg #1')
      OR "item"."i_brand" IN (
        'scholaramalgamalg #14',
        'scholaramalgamalg #7',
        'exportiunivamalg #9',
        'scholaramalgamalg #9'
      )
    )
    AND (
      "item"."i_brand" IN ('amalgimporto #1', 'edu packscholar #1', 'exportiimporto #1', 'importoamalg #1')
      OR "item"."i_category" IN ('Books', 'Children', 'Electronics')
    )
    AND (
      "item"."i_brand" IN ('amalgimporto #1', 'edu packscholar #1', 'exportiimporto #1', 'importoamalg #1')
      OR "item"."i_class" IN ('personal', 'portable', 'reference', 'self-help')
    )
    AND (
      "item"."i_brand" IN (
        'scholaramalgamalg #14',
        'scholaramalgamalg #7',
        'exportiunivamalg #9',
        'scholaramalgamalg #9'
      )
      OR "item"."i_category" IN ('Women', 'Music', 'Men')
    )
    AND (
      "item"."i_brand" IN (
        'scholaramalgamalg #14',
        'scholaramalgamalg #7',
        'exportiunivamalg #9',
        'scholaramalgamalg #9'
      )
      OR "item"."i_class" IN ('accessories', 'classical', 'fragrances', 'pants')
    )
    AND (
      "item"."i_category" IN ('Books', 'Children', 'Electronics')
      OR "item"."i_category" IN ('Women', 'Music', 'Men')
    )
    AND (
      "item"."i_category" IN ('Books', 'Children', 'Electronics')
      OR "item"."i_class" IN ('accessories', 'classical', 'fragrances', 'pants')
    )
    AND (
      "item"."i_category" IN ('Women', 'Music', 'Men')
      OR "item"."i_class" IN ('personal', 'portable', 'reference', 'self-help')
    )
    AND (
      "item"."i_class" IN ('accessories', 'classical', 'fragrances', 'pants')
      OR "item"."i_class" IN ('personal', 'portable', 'reference', 'self-help')
    )
  GROUP BY
    "item"."i_manager_id",
    "date_dim"."d_moy"
)
SELECT
  "tmp1"."i_manager_id" AS "i_manager_id",
  "tmp1"."sum_sales" AS "sum_sales",
  "tmp1"."avg_monthly_sales" AS "avg_monthly_sales"
FROM "tmp1" AS "tmp1"
WHERE
  CASE
    WHEN "tmp1"."avg_monthly_sales" > 0
    THEN ABS("tmp1"."sum_sales" - "tmp1"."avg_monthly_sales") / "tmp1"."avg_monthly_sales"
    ELSE NULL
  END > 0.1
ORDER BY
  "tmp1"."i_manager_id",
  "tmp1"."avg_monthly_sales",
  "tmp1"."sum_sales"
LIMIT 100;
