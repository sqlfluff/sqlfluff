--------------------------------------
-- TPC-DS 75
--------------------------------------
WITH all_sales
     AS (SELECT d_year,
                i_brand_id,
                i_class_id,
                i_category_id,
                i_manufact_id,
                Sum(sales_cnt) AS sales_cnt,
                Sum(sales_amt) AS sales_amt
         FROM   (SELECT d_year,
                        i_brand_id,
                        i_class_id,
                        i_category_id,
                        i_manufact_id,
                        cs_quantity - COALESCE(cr_return_quantity, 0)        AS
                        sales_cnt,
                        cs_ext_sales_price - COALESCE(cr_return_amount, 0.0) AS
                        sales_amt
                 FROM   catalog_sales
                        JOIN item
                          ON i_item_sk = cs_item_sk
                        JOIN date_dim
                          ON d_date_sk = cs_sold_date_sk
                        LEFT JOIN catalog_returns
                               ON ( cs_order_number = cr_order_number
                                    AND cs_item_sk = cr_item_sk )
                 WHERE  i_category = 'Men'
                 UNION
                 SELECT d_year,
                        i_brand_id,
                        i_class_id,
                        i_category_id,
                        i_manufact_id,
                        ss_quantity - COALESCE(sr_return_quantity, 0)     AS
                        sales_cnt,
                        ss_ext_sales_price - COALESCE(sr_return_amt, 0.0) AS
                        sales_amt
                 FROM   store_sales
                        JOIN item
                          ON i_item_sk = ss_item_sk
                        JOIN date_dim
                          ON d_date_sk = ss_sold_date_sk
                        LEFT JOIN store_returns
                               ON ( ss_ticket_number = sr_ticket_number
                                    AND ss_item_sk = sr_item_sk )
                 WHERE  i_category = 'Men'
                 UNION
                 SELECT d_year,
                        i_brand_id,
                        i_class_id,
                        i_category_id,
                        i_manufact_id,
                        ws_quantity - COALESCE(wr_return_quantity, 0)     AS
                        sales_cnt,
                        ws_ext_sales_price - COALESCE(wr_return_amt, 0.0) AS
                        sales_amt
                 FROM   web_sales
                        JOIN item
                          ON i_item_sk = ws_item_sk
                        JOIN date_dim
                          ON d_date_sk = ws_sold_date_sk
                        LEFT JOIN web_returns
                               ON ( ws_order_number = wr_order_number
                                    AND ws_item_sk = wr_item_sk )
                 WHERE  i_category = 'Men') sales_detail
         GROUP  BY d_year,
                   i_brand_id,
                   i_class_id,
                   i_category_id,
                   i_manufact_id)
SELECT prev_yr.d_year                        AS prev_year,
               curr_yr.d_year                        AS year1,
               curr_yr.i_brand_id,
               curr_yr.i_class_id,
               curr_yr.i_category_id,
               curr_yr.i_manufact_id,
               prev_yr.sales_cnt                     AS prev_yr_cnt,
               curr_yr.sales_cnt                     AS curr_yr_cnt,
               curr_yr.sales_cnt - prev_yr.sales_cnt AS sales_cnt_diff,
               curr_yr.sales_amt - prev_yr.sales_amt AS sales_amt_diff
FROM   all_sales curr_yr,
       all_sales prev_yr
WHERE  curr_yr.i_brand_id = prev_yr.i_brand_id
       AND curr_yr.i_class_id = prev_yr.i_class_id
       AND curr_yr.i_category_id = prev_yr.i_category_id
       AND curr_yr.i_manufact_id = prev_yr.i_manufact_id
       AND curr_yr.d_year = 2002
       AND prev_yr.d_year = 2002 - 1
       AND Cast(curr_yr.sales_cnt AS DECIMAL(17, 2)) / Cast(prev_yr.sales_cnt AS
                                                                DECIMAL(17, 2))
           < 0.9
ORDER  BY sales_cnt_diff
LIMIT 100;
WITH "item_2" AS (
  SELECT
    "item"."i_item_sk" AS "i_item_sk",
    "item"."i_brand_id" AS "i_brand_id",
    "item"."i_class_id" AS "i_class_id",
    "item"."i_category_id" AS "i_category_id",
    "item"."i_category" AS "i_category",
    "item"."i_manufact_id" AS "i_manufact_id"
  FROM "item" AS "item"
  WHERE
    "item"."i_category" = 'Men'
), "date_dim_2" AS (
  SELECT
    "date_dim"."d_date_sk" AS "d_date_sk",
    "date_dim"."d_year" AS "d_year"
  FROM "date_dim" AS "date_dim"
), "sales_detail" AS (
  SELECT
    "date_dim"."d_year" AS "d_year",
    "item"."i_brand_id" AS "i_brand_id",
    "item"."i_class_id" AS "i_class_id",
    "item"."i_category_id" AS "i_category_id",
    "item"."i_manufact_id" AS "i_manufact_id",
    "catalog_sales"."cs_quantity" - COALESCE("catalog_returns"."cr_return_quantity", 0) AS "sales_cnt",
    "catalog_sales"."cs_ext_sales_price" - COALESCE("catalog_returns"."cr_return_amount", 0.0) AS "sales_amt"
  FROM "catalog_sales" AS "catalog_sales"
  JOIN "item_2" AS "item"
    ON "catalog_sales"."cs_item_sk" = "item"."i_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "catalog_sales"."cs_sold_date_sk" = "date_dim"."d_date_sk"
  LEFT JOIN "catalog_returns" AS "catalog_returns"
    ON "catalog_returns"."cr_item_sk" = "catalog_sales"."cs_item_sk"
    AND "catalog_returns"."cr_order_number" = "catalog_sales"."cs_order_number"
  UNION
  SELECT
    "date_dim"."d_year" AS "d_year",
    "item"."i_brand_id" AS "i_brand_id",
    "item"."i_class_id" AS "i_class_id",
    "item"."i_category_id" AS "i_category_id",
    "item"."i_manufact_id" AS "i_manufact_id",
    "store_sales"."ss_quantity" - COALESCE("store_returns"."sr_return_quantity", 0) AS "sales_cnt",
    "store_sales"."ss_ext_sales_price" - COALESCE("store_returns"."sr_return_amt", 0.0) AS "sales_amt"
  FROM "store_sales" AS "store_sales"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "store_sales"."ss_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  LEFT JOIN "store_returns" AS "store_returns"
    ON "store_returns"."sr_item_sk" = "store_sales"."ss_item_sk"
    AND "store_returns"."sr_ticket_number" = "store_sales"."ss_ticket_number"
  UNION
  SELECT
    "date_dim"."d_year" AS "d_year",
    "item"."i_brand_id" AS "i_brand_id",
    "item"."i_class_id" AS "i_class_id",
    "item"."i_category_id" AS "i_category_id",
    "item"."i_manufact_id" AS "i_manufact_id",
    "web_sales"."ws_quantity" - COALESCE("web_returns"."wr_return_quantity", 0) AS "sales_cnt",
    "web_sales"."ws_ext_sales_price" - COALESCE("web_returns"."wr_return_amt", 0.0) AS "sales_amt"
  FROM "web_sales" AS "web_sales"
  JOIN "item_2" AS "item"
    ON "item"."i_item_sk" = "web_sales"."ws_item_sk"
  JOIN "date_dim_2" AS "date_dim"
    ON "date_dim"."d_date_sk" = "web_sales"."ws_sold_date_sk"
  LEFT JOIN "web_returns" AS "web_returns"
    ON "web_returns"."wr_item_sk" = "web_sales"."ws_item_sk"
    AND "web_returns"."wr_order_number" = "web_sales"."ws_order_number"
), "all_sales" AS (
  SELECT
    "sales_detail"."d_year" AS "d_year",
    "sales_detail"."i_brand_id" AS "i_brand_id",
    "sales_detail"."i_class_id" AS "i_class_id",
    "sales_detail"."i_category_id" AS "i_category_id",
    "sales_detail"."i_manufact_id" AS "i_manufact_id",
    SUM("sales_detail"."sales_cnt") AS "sales_cnt",
    SUM("sales_detail"."sales_amt") AS "sales_amt"
  FROM "sales_detail" AS "sales_detail"
  GROUP BY
    "sales_detail"."d_year",
    "sales_detail"."i_brand_id",
    "sales_detail"."i_class_id",
    "sales_detail"."i_category_id",
    "sales_detail"."i_manufact_id"
)
SELECT
  "prev_yr"."d_year" AS "prev_year",
  "curr_yr"."d_year" AS "year1",
  "curr_yr"."i_brand_id" AS "i_brand_id",
  "curr_yr"."i_class_id" AS "i_class_id",
  "curr_yr"."i_category_id" AS "i_category_id",
  "curr_yr"."i_manufact_id" AS "i_manufact_id",
  "prev_yr"."sales_cnt" AS "prev_yr_cnt",
  "curr_yr"."sales_cnt" AS "curr_yr_cnt",
  "curr_yr"."sales_cnt" - "prev_yr"."sales_cnt" AS "sales_cnt_diff",
  "curr_yr"."sales_amt" - "prev_yr"."sales_amt" AS "sales_amt_diff"
FROM "all_sales" AS "curr_yr"
JOIN "all_sales" AS "prev_yr"
  ON "curr_yr"."i_brand_id" = "prev_yr"."i_brand_id"
  AND "curr_yr"."i_category_id" = "prev_yr"."i_category_id"
  AND "curr_yr"."i_class_id" = "prev_yr"."i_class_id"
  AND "curr_yr"."i_manufact_id" = "prev_yr"."i_manufact_id"
  AND "prev_yr"."d_year" = 2001
  AND CAST("curr_yr"."sales_cnt" AS DECIMAL(17, 2)) / CAST("prev_yr"."sales_cnt" AS DECIMAL(17, 2)) < 0.9
WHERE
  "curr_yr"."d_year" = 2002
ORDER BY
  "sales_cnt_diff"
LIMIT 100;
