--------------------------------------
-- TPC-DS 2
--------------------------------------
WITH wscs
     AS (SELECT sold_date_sk,
                sales_price
         FROM   (SELECT ws_sold_date_sk    sold_date_sk,
                        ws_ext_sales_price sales_price
                 FROM   web_sales)
         UNION ALL
         (SELECT cs_sold_date_sk    sold_date_sk,
                 cs_ext_sales_price sales_price
          FROM   catalog_sales)),
     wswscs
     AS (SELECT d_week_seq,
                Sum(CASE
                      WHEN ( d_day_name = 'Sunday' ) THEN sales_price
                      ELSE NULL
                    END) sun_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Monday' ) THEN sales_price
                      ELSE NULL
                    END) mon_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Tuesday' ) THEN sales_price
                      ELSE NULL
                    END) tue_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Wednesday' ) THEN sales_price
                      ELSE NULL
                    END) wed_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Thursday' ) THEN sales_price
                      ELSE NULL
                    END) thu_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Friday' ) THEN sales_price
                      ELSE NULL
                    END) fri_sales,
                Sum(CASE
                      WHEN ( d_day_name = 'Saturday' ) THEN sales_price
                      ELSE NULL
                    END) sat_sales
         FROM   wscs,
                date_dim
         WHERE  d_date_sk = sold_date_sk
         GROUP  BY d_week_seq)
SELECT d_week_seq1,
       Round(sun_sales1 / sun_sales2, 2) AS "_col_1",
       Round(mon_sales1 / mon_sales2, 2) AS "_col_2",
       Round(tue_sales1 / tue_sales2, 2) AS "_col_3",
       Round(wed_sales1 / wed_sales2, 2) AS "_col_4",
       Round(thu_sales1 / thu_sales2, 2) AS "_col_5",
       Round(fri_sales1 / fri_sales2, 2) AS "_col_6",
       Round(sat_sales1 / sat_sales2, 2) AS "_col_7"
FROM   (SELECT wswscs.d_week_seq d_week_seq1,
               sun_sales         sun_sales1,
               mon_sales         mon_sales1,
               tue_sales         tue_sales1,
               wed_sales         wed_sales1,
               thu_sales         thu_sales1,
               fri_sales         fri_sales1,
               sat_sales         sat_sales1
        FROM   wswscs,
               date_dim
        WHERE  date_dim.d_week_seq = wswscs.d_week_seq
               AND d_year = 1998) y,
       (SELECT wswscs.d_week_seq d_week_seq2,
               sun_sales         sun_sales2,
               mon_sales         mon_sales2,
               tue_sales         tue_sales2,
               wed_sales         wed_sales2,
               thu_sales         thu_sales2,
               fri_sales         fri_sales2,
               sat_sales         sat_sales2
        FROM   wswscs,
               date_dim
        WHERE  date_dim.d_week_seq = wswscs.d_week_seq
               AND d_year = 1998 + 1) z
WHERE  d_week_seq1 = d_week_seq2 - 53
ORDER  BY d_week_seq1;
WITH "wscs" AS (
  SELECT
    "web_sales"."ws_sold_date_sk" AS "sold_date_sk",
    "web_sales"."ws_ext_sales_price" AS "sales_price"
  FROM "web_sales" AS "web_sales"
  UNION ALL
  (
    SELECT
      "catalog_sales"."cs_sold_date_sk" AS "sold_date_sk",
      "catalog_sales"."cs_ext_sales_price" AS "sales_price"
    FROM "catalog_sales" AS "catalog_sales"
  )
), "wswscs" AS (
  SELECT
    "date_dim"."d_week_seq" AS "d_week_seq",
    SUM(
      CASE WHEN "date_dim"."d_day_name" = 'Sunday' THEN "wscs"."sales_price" ELSE NULL END
    ) AS "sun_sales",
    SUM(
      CASE WHEN "date_dim"."d_day_name" = 'Monday' THEN "wscs"."sales_price" ELSE NULL END
    ) AS "mon_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Tuesday'
        THEN "wscs"."sales_price"
        ELSE NULL
      END
    ) AS "tue_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Wednesday'
        THEN "wscs"."sales_price"
        ELSE NULL
      END
    ) AS "wed_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Thursday'
        THEN "wscs"."sales_price"
        ELSE NULL
      END
    ) AS "thu_sales",
    SUM(
      CASE WHEN "date_dim"."d_day_name" = 'Friday' THEN "wscs"."sales_price" ELSE NULL END
    ) AS "fri_sales",
    SUM(
      CASE
        WHEN "date_dim"."d_day_name" = 'Saturday'
        THEN "wscs"."sales_price"
        ELSE NULL
      END
    ) AS "sat_sales"
  FROM "wscs" AS "wscs"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "wscs"."sold_date_sk"
  GROUP BY
    "date_dim"."d_week_seq"
), "z" AS (
  SELECT
    "wswscs"."d_week_seq" AS "d_week_seq2",
    "wswscs"."sun_sales" AS "sun_sales2",
    "wswscs"."mon_sales" AS "mon_sales2",
    "wswscs"."tue_sales" AS "tue_sales2",
    "wswscs"."wed_sales" AS "wed_sales2",
    "wswscs"."thu_sales" AS "thu_sales2",
    "wswscs"."fri_sales" AS "fri_sales2",
    "wswscs"."sat_sales" AS "sat_sales2"
  FROM "wswscs" AS "wswscs"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_week_seq" = "wswscs"."d_week_seq" AND "date_dim"."d_year" = 1999
)
SELECT
  "wswscs"."d_week_seq" AS "d_week_seq1",
  ROUND("wswscs"."sun_sales" / "z"."sun_sales2", 2) AS "_col_1",
  ROUND("wswscs"."mon_sales" / "z"."mon_sales2", 2) AS "_col_2",
  ROUND("wswscs"."tue_sales" / "z"."tue_sales2", 2) AS "_col_3",
  ROUND("wswscs"."wed_sales" / "z"."wed_sales2", 2) AS "_col_4",
  ROUND("wswscs"."thu_sales" / "z"."thu_sales2", 2) AS "_col_5",
  ROUND("wswscs"."fri_sales" / "z"."fri_sales2", 2) AS "_col_6",
  ROUND("wswscs"."sat_sales" / "z"."sat_sales2", 2) AS "_col_7"
FROM "wswscs" AS "wswscs"
JOIN "date_dim" AS "date_dim"
  ON "date_dim"."d_week_seq" = "wswscs"."d_week_seq" AND "date_dim"."d_year" = 1998
JOIN "z" AS "z"
  ON "wswscs"."d_week_seq" = "z"."d_week_seq2" - 53
ORDER BY
  "d_week_seq1";
