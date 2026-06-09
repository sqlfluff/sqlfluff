--------------------------------------
-- TPC-DS 36
--------------------------------------
SELECT Sum(ss_net_profit) / Sum(ss_ext_sales_price)                 AS
               gross_margin,
               i_category,
               i_class,
               Grouping(i_category) + Grouping(i_class)                     AS
               lochierarchy,
               Rank()
                 OVER (
                   partition BY Grouping(i_category)+Grouping(i_class), CASE
                 WHEN Grouping(
                 i_class) = 0 THEN i_category END
                   ORDER BY Sum(ss_net_profit)/Sum(ss_ext_sales_price) ASC) AS
               rank_within_parent
FROM   store_sales,
       date_dim d1,
       item,
       store
WHERE  d1.d_year = 2000
       AND d1.d_date_sk = ss_sold_date_sk
       AND i_item_sk = ss_item_sk
       AND s_store_sk = ss_store_sk
       AND s_state IN ( 'TN', 'TN', 'TN', 'TN',
                        'TN', 'TN', 'TN', 'TN' )
GROUP  BY rollup( i_category, i_class )
ORDER  BY lochierarchy DESC,
          CASE
            WHEN lochierarchy = 0 THEN i_category
          END,
          rank_within_parent
LIMIT 100;
SELECT
  SUM("store_sales"."ss_net_profit") / SUM("store_sales"."ss_ext_sales_price") AS "gross_margin",
  "item"."i_category" AS "i_category",
  "item"."i_class" AS "i_class",
  GROUPING("item"."i_category") + GROUPING("item"."i_class") AS "lochierarchy",
  RANK() OVER (
    PARTITION BY GROUPING("item"."i_category") + GROUPING("item"."i_class"), CASE WHEN GROUPING("item"."i_class") = 0 THEN "item"."i_category" END
    ORDER BY SUM("store_sales"."ss_net_profit") / SUM("store_sales"."ss_ext_sales_price")
  ) AS "rank_within_parent"
FROM "store_sales" AS "store_sales"
JOIN "date_dim" AS "d1"
  ON "d1"."d_date_sk" = "store_sales"."ss_sold_date_sk" AND "d1"."d_year" = 2000
JOIN "item" AS "item"
  ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
JOIN "store" AS "store"
  ON "store"."s_state" IN ('TN', 'TN', 'TN', 'TN', 'TN', 'TN', 'TN', 'TN')
  AND "store"."s_store_sk" = "store_sales"."ss_store_sk"
GROUP BY
  ROLLUP (
    "item"."i_category",
    "item"."i_class"
  )
ORDER BY
  "lochierarchy" DESC,
  CASE WHEN "lochierarchy" = 0 THEN "i_category" END,
  "rank_within_parent"
LIMIT 100;
