--------------------------------------
-- TPC-DS 28
--------------------------------------
SELECT *
FROM   (SELECT Avg(ss_list_price)            b1_lp,
               Count(ss_list_price)          b1_cnt,
               Count(DISTINCT ss_list_price) b1_cntd
        FROM   store_sales
        WHERE  ss_quantity BETWEEN 0 AND 5
               AND ( ss_list_price BETWEEN 18 AND 18 + 10
                      OR ss_coupon_amt BETWEEN 1939 AND 1939 + 1000
                      OR ss_wholesale_cost BETWEEN 34 AND 34 + 20 )) B1,
       (SELECT Avg(ss_list_price)            b2_lp,
               Count(ss_list_price)          b2_cnt,
               Count(DISTINCT ss_list_price) b2_cntd
        FROM   store_sales
        WHERE  ss_quantity BETWEEN 6 AND 10
               AND ( ss_list_price BETWEEN 1 AND 1 + 10
                      OR ss_coupon_amt BETWEEN 35 AND 35 + 1000
                      OR ss_wholesale_cost BETWEEN 50 AND 50 + 20 )) B2,
       (SELECT Avg(ss_list_price)            b3_lp,
               Count(ss_list_price)          b3_cnt,
               Count(DISTINCT ss_list_price) b3_cntd
        FROM   store_sales
        WHERE  ss_quantity BETWEEN 11 AND 15
               AND ( ss_list_price BETWEEN 91 AND 91 + 10
                      OR ss_coupon_amt BETWEEN 1412 AND 1412 + 1000
                      OR ss_wholesale_cost BETWEEN 17 AND 17 + 20 )) B3,
       (SELECT Avg(ss_list_price)            b4_lp,
               Count(ss_list_price)          b4_cnt,
               Count(DISTINCT ss_list_price) b4_cntd
        FROM   store_sales
        WHERE  ss_quantity BETWEEN 16 AND 20
               AND ( ss_list_price BETWEEN 9 AND 9 + 10
                      OR ss_coupon_amt BETWEEN 5270 AND 5270 + 1000
                      OR ss_wholesale_cost BETWEEN 29 AND 29 + 20 )) B4,
       (SELECT Avg(ss_list_price)            b5_lp,
               Count(ss_list_price)          b5_cnt,
               Count(DISTINCT ss_list_price) b5_cntd
        FROM   store_sales
        WHERE  ss_quantity BETWEEN 21 AND 25
               AND ( ss_list_price BETWEEN 45 AND 45 + 10
                      OR ss_coupon_amt BETWEEN 826 AND 826 + 1000
                      OR ss_wholesale_cost BETWEEN 5 AND 5 + 20 )) B5,
       (SELECT Avg(ss_list_price)            b6_lp,
               Count(ss_list_price)          b6_cnt,
               Count(DISTINCT ss_list_price) b6_cntd
        FROM   store_sales
        WHERE  ss_quantity BETWEEN 26 AND 30
               AND ( ss_list_price BETWEEN 174 AND 174 + 10
                      OR ss_coupon_amt BETWEEN 5548 AND 5548 + 1000
                      OR ss_wholesale_cost BETWEEN 42 AND 42 + 20 )) B6
LIMIT 100;
WITH "b1" AS (
  SELECT
    AVG("store_sales"."ss_list_price") AS "b1_lp",
    COUNT("store_sales"."ss_list_price") AS "b1_cnt",
    COUNT(DISTINCT "store_sales"."ss_list_price") AS "b1_cntd"
  FROM "store_sales" AS "store_sales"
  WHERE
    (
      "store_sales"."ss_coupon_amt" <= 2939
      AND "store_sales"."ss_coupon_amt" >= 1939
      OR "store_sales"."ss_list_price" <= 28
      AND "store_sales"."ss_list_price" >= 18
      OR "store_sales"."ss_wholesale_cost" <= 54
      AND "store_sales"."ss_wholesale_cost" >= 34
    )
    AND "store_sales"."ss_quantity" <= 5
    AND "store_sales"."ss_quantity" >= 0
), "b2" AS (
  SELECT
    AVG("store_sales"."ss_list_price") AS "b2_lp",
    COUNT("store_sales"."ss_list_price") AS "b2_cnt",
    COUNT(DISTINCT "store_sales"."ss_list_price") AS "b2_cntd"
  FROM "store_sales" AS "store_sales"
  WHERE
    (
      "store_sales"."ss_coupon_amt" <= 1035
      AND "store_sales"."ss_coupon_amt" >= 35
      OR "store_sales"."ss_list_price" <= 11
      AND "store_sales"."ss_list_price" >= 1
      OR "store_sales"."ss_wholesale_cost" <= 70
      AND "store_sales"."ss_wholesale_cost" >= 50
    )
    AND "store_sales"."ss_quantity" <= 10
    AND "store_sales"."ss_quantity" >= 6
), "b3" AS (
  SELECT
    AVG("store_sales"."ss_list_price") AS "b3_lp",
    COUNT("store_sales"."ss_list_price") AS "b3_cnt",
    COUNT(DISTINCT "store_sales"."ss_list_price") AS "b3_cntd"
  FROM "store_sales" AS "store_sales"
  WHERE
    (
      "store_sales"."ss_coupon_amt" <= 2412
      AND "store_sales"."ss_coupon_amt" >= 1412
      OR "store_sales"."ss_list_price" <= 101
      AND "store_sales"."ss_list_price" >= 91
      OR "store_sales"."ss_wholesale_cost" <= 37
      AND "store_sales"."ss_wholesale_cost" >= 17
    )
    AND "store_sales"."ss_quantity" <= 15
    AND "store_sales"."ss_quantity" >= 11
), "b4" AS (
  SELECT
    AVG("store_sales"."ss_list_price") AS "b4_lp",
    COUNT("store_sales"."ss_list_price") AS "b4_cnt",
    COUNT(DISTINCT "store_sales"."ss_list_price") AS "b4_cntd"
  FROM "store_sales" AS "store_sales"
  WHERE
    (
      "store_sales"."ss_coupon_amt" <= 6270
      AND "store_sales"."ss_coupon_amt" >= 5270
      OR "store_sales"."ss_list_price" <= 19
      AND "store_sales"."ss_list_price" >= 9
      OR "store_sales"."ss_wholesale_cost" <= 49
      AND "store_sales"."ss_wholesale_cost" >= 29
    )
    AND "store_sales"."ss_quantity" <= 20
    AND "store_sales"."ss_quantity" >= 16
), "b5" AS (
  SELECT
    AVG("store_sales"."ss_list_price") AS "b5_lp",
    COUNT("store_sales"."ss_list_price") AS "b5_cnt",
    COUNT(DISTINCT "store_sales"."ss_list_price") AS "b5_cntd"
  FROM "store_sales" AS "store_sales"
  WHERE
    (
      "store_sales"."ss_coupon_amt" <= 1826
      AND "store_sales"."ss_coupon_amt" >= 826
      OR "store_sales"."ss_list_price" <= 55
      AND "store_sales"."ss_list_price" >= 45
      OR "store_sales"."ss_wholesale_cost" <= 25
      AND "store_sales"."ss_wholesale_cost" >= 5
    )
    AND "store_sales"."ss_quantity" <= 25
    AND "store_sales"."ss_quantity" >= 21
), "b6" AS (
  SELECT
    AVG("store_sales"."ss_list_price") AS "b6_lp",
    COUNT("store_sales"."ss_list_price") AS "b6_cnt",
    COUNT(DISTINCT "store_sales"."ss_list_price") AS "b6_cntd"
  FROM "store_sales" AS "store_sales"
  WHERE
    (
      "store_sales"."ss_coupon_amt" <= 6548
      AND "store_sales"."ss_coupon_amt" >= 5548
      OR "store_sales"."ss_list_price" <= 184
      AND "store_sales"."ss_list_price" >= 174
      OR "store_sales"."ss_wholesale_cost" <= 62
      AND "store_sales"."ss_wholesale_cost" >= 42
    )
    AND "store_sales"."ss_quantity" <= 30
    AND "store_sales"."ss_quantity" >= 26
)
SELECT
  "b1"."b1_lp" AS "b1_lp",
  "b1"."b1_cnt" AS "b1_cnt",
  "b1"."b1_cntd" AS "b1_cntd",
  "b2"."b2_lp" AS "b2_lp",
  "b2"."b2_cnt" AS "b2_cnt",
  "b2"."b2_cntd" AS "b2_cntd",
  "b3"."b3_lp" AS "b3_lp",
  "b3"."b3_cnt" AS "b3_cnt",
  "b3"."b3_cntd" AS "b3_cntd",
  "b4"."b4_lp" AS "b4_lp",
  "b4"."b4_cnt" AS "b4_cnt",
  "b4"."b4_cntd" AS "b4_cntd",
  "b5"."b5_lp" AS "b5_lp",
  "b5"."b5_cnt" AS "b5_cnt",
  "b5"."b5_cntd" AS "b5_cntd",
  "b6"."b6_lp" AS "b6_lp",
  "b6"."b6_cnt" AS "b6_cnt",
  "b6"."b6_cntd" AS "b6_cntd"
FROM "b1" AS "b1"
CROSS JOIN "b2" AS "b2"
CROSS JOIN "b3" AS "b3"
CROSS JOIN "b4" AS "b4"
CROSS JOIN "b5" AS "b5"
CROSS JOIN "b6" AS "b6"
LIMIT 100;
