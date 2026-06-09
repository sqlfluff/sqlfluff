--------------------------------------
-- TPC-DS 59
--------------------------------------
WITH wss
     AS (SELECT d_week_seq,
                ss_store_sk,
                Sum(CASE
                      WHEN ( d_day_name = 'Sunday' ) THEN ss_sales_price
                      ELSE NULL
                    END) sun_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Monday' ) THEN ss_sales_price
                      ELSE NULL
                    END) mon_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Tuesday' ) THEN ss_sales_price
                      ELSE NULL
                    END) tue_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Wednesday' ) THEN ss_sales_price
                      ELSE NULL
                    END) wed_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Thursday' ) THEN ss_sales_price
                      ELSE NULL
                    END) thu_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Friday' ) THEN ss_sales_price
                      ELSE NULL
                    END) fri_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Saturday' ) THEN ss_sales_price
                      ELSE NULL
                    END) sat_sales
         FROM   store_sales,
                date_dim
         WHERE  d_date_sk = ss_sold_date_sk
         GROUP  BY d_week_seq,
                   ss_store_sk)
SELECT s_store_name1,
               s_store_id1,
               d_week_seq1,
               sun_sales1 / sun_sales2 AS "_col_3",
               mon_sales1 / mon_sales2 AS "_col_4",
               tue_sales1 / tue_sales2 AS "_col_5",
               wed_sales1 / wed_sales2 AS "_col_6",
               thu_sales1 / thu_sales2 AS "_col_7",
               fri_sales1 / fri_sales2 AS "_col_8",
               sat_sales1 / sat_sales2 AS "_col_9"
FROM   (SELECT s_store_name   s_store_name1,
               wss.d_week_seq d_week_seq1,
               s_store_id     s_store_id1,
               sun_sales      sun_sales1,
               mon_sales      mon_sales1,
               tue_sales      tue_sales1,
               wed_sales      wed_sales1,
               thu_sales      thu_sales1,
               fri_sales      fri_sales1,
               sat_sales      sat_sales1
        FROM   wss,
               store,
               date_dim d
        WHERE  d.d_week_seq = wss.d_week_seq
               AND ss_store_sk = s_store_sk
               AND d_month_seq BETWEEN 1196 AND 1196 + 11) y,
       (SELECT s_store_name   s_store_name2,
               wss.d_week_seq d_week_seq2,
               s_store_id     s_store_id2,
               sun_sales      sun_sales2,
               mon_sales      mon_sales2,
               tue_sales      tue_sales2,
               wed_sales      wed_sales2,
               thu_sales      thu_sales2,
               fri_sales      fri_sales2,
               sat_sales      sat_sales2
        FROM   wss,
               store,
               date_dim d
        WHERE  d.d_week_seq = wss.d_week_seq
               AND ss_store_sk = s_store_sk
               AND d_month_seq BETWEEN 1196 + 12 AND 1196 + 23) x
WHERE  s_store_id1 = s_store_id2
       AND d_week_seq1 = d_week_seq2 - 52
ORDER  BY s_store_name1,
          s_store_id1,
          d_week_seq1
LIMIT 100;
WITH "wss" AS (
  SELECT
    "date_dim"."d_week_seq" AS "d_week_seq",
    "store_sales"."ss_store_sk" AS "ss_store_sk",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Sunday'
        THEN "store_sales"."ss_sales_price"
        ELSE NULL
      END
    ) AS "sun_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Monday'
        THEN "store_sales"."ss_sales_price"
        ELSE NULL
      END
    ) AS "mon_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Tuesday'
        THEN "store_sales"."ss_sales_price"
        ELSE NULL
      END
    ) AS "tue_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Wednesday'
        THEN "store_sales"."ss_sales_price"
        ELSE NULL
      END
    ) AS "wed_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Thursday'
        THEN "store_sales"."ss_sales_price"
        ELSE NULL
      END
    ) AS "thu_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Friday'
        THEN "store_sales"."ss_sales_price"
        ELSE NULL
      END
    ) AS "fri_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Saturday'
        THEN "store_sales"."ss_sales_price"
        ELSE NULL
      END
    ) AS "sat_sales"
  FROM "store_sales" AS "store_sales"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  GROUP BY
    "date_dim"."d_week_seq",
    "store_sales"."ss_store_sk"
), "x" AS (
  SELECT
    "wss"."d_week_seq" AS "d_week_seq2",
    "store"."s_store_id" AS "s_store_id2",
    "wss"."sun_sales" AS "sun_sales2",
    "wss"."mon_sales" AS "mon_sales2",
    "wss"."tue_sales" AS "tue_sales2",
    "wss"."wed_sales" AS "wed_sales2",
    "wss"."thu_sales" AS "thu_sales2",
    "wss"."fri_sales" AS "fri_sales2",
    "wss"."sat_sales" AS "sat_sales2"
  FROM "wss" AS "wss"
  JOIN "date_dim" AS "d"
    ON "d"."d_month_seq" <= 1219
    AND "d"."d_month_seq" >= 1208
    AND "d"."d_week_seq" = "wss"."d_week_seq"
  JOIN "store" AS "store"
    ON "store"."s_store_sk" = "wss"."ss_store_sk"
)
SELECT
  "store"."s_store_name" AS "s_store_name1",
  "store"."s_store_id" AS "s_store_id1",
  "wss"."d_week_seq" AS "d_week_seq1",
  "wss"."sun_sales" / "x"."sun_sales2" AS "_col_3",
  "wss"."mon_sales" / "x"."mon_sales2" AS "_col_4",
  "wss"."tue_sales" / "x"."tue_sales2" AS "_col_5",
  "wss"."wed_sales" / "x"."wed_sales2" AS "_col_6",
  "wss"."thu_sales" / "x"."thu_sales2" AS "_col_7",
  "wss"."fri_sales" / "x"."fri_sales2" AS "_col_8",
  "wss"."sat_sales" / "x"."sat_sales2" AS "_col_9"
FROM "wss" AS "wss"
JOIN "date_dim" AS "d"
  ON "d"."d_month_seq" <= 1207
  AND "d"."d_month_seq" >= 1196
  AND "d"."d_week_seq" = "wss"."d_week_seq"
JOIN "store" AS "store"
  ON "store"."s_store_sk" = "wss"."ss_store_sk"
JOIN "x" AS "x"
  ON "store"."s_store_id" = "x"."s_store_id2"
  AND "wss"."d_week_seq" = "x"."d_week_seq2" - 52
ORDER BY
  "s_store_name1",
  "s_store_id1",
  "d_week_seq1"
LIMIT 100;
