--------------------------------------
-- TPC-DS 70
--------------------------------------
SELECT Sum(ss_net_profit)                     AS total_sum,
               s_state,
               s_county,
               Grouping(s_state) + Grouping(s_county) AS lochierarchy,
               Rank()
                 OVER (
                   partition BY Grouping(s_state)+Grouping(s_county), CASE WHEN
                 Grouping(
                 s_county) = 0 THEN s_state END
                   ORDER BY Sum(ss_net_profit) DESC)  AS rank_within_parent
FROM   store_sales,
       date_dim d1,
       store
WHERE  d1.d_month_seq BETWEEN 1200 AND 1200 + 11
       AND d1.d_date_sk = ss_sold_date_sk
       AND s_store_sk = ss_store_sk
       AND s_state IN (SELECT s_state
                       FROM   (SELECT s_state                               AS
                                      s_state,
                                      Rank()
                                        OVER (
                                          partition BY s_state
                                          ORDER BY Sum(ss_net_profit) DESC) AS
                                      ranking
                               FROM   store_sales,
                                      store,
                                      date_dim
                               WHERE  d_month_seq BETWEEN 1200 AND 1200 + 11
                                      AND d_date_sk = ss_sold_date_sk
                                      AND s_store_sk = ss_store_sk
                               GROUP  BY s_state) tmp1
                       WHERE  ranking <= 5)
GROUP  BY rollup( s_state, s_county )
ORDER  BY lochierarchy DESC,
          CASE
            WHEN lochierarchy = 0 THEN s_state
          END,
          rank_within_parent
LIMIT 100;
WITH "store_sales_2" AS (
  SELECT
    "store_sales"."ss_sold_date_sk" AS "ss_sold_date_sk",
    "store_sales"."ss_store_sk" AS "ss_store_sk",
    "store_sales"."ss_net_profit" AS "ss_net_profit"
  FROM "store_sales" AS "store_sales"
), "tmp1" AS (
  SELECT
    "store"."s_state" AS "s_state",
    RANK() OVER (PARTITION BY "store"."s_state" ORDER BY SUM("store_sales"."ss_net_profit") DESC) AS "ranking"
  FROM "store_sales_2" AS "store_sales"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_sales"."ss_sold_date_sk"
    AND "date_dim"."d_month_seq" <= 1211
    AND "date_dim"."d_month_seq" >= 1200
  JOIN "store" AS "store"
    ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
  GROUP BY
    "store"."s_state"
), "_u_0" AS (
  SELECT
    "tmp1"."s_state" AS "s_state"
  FROM "tmp1" AS "tmp1"
  WHERE
    "tmp1"."ranking" <= 5
  GROUP BY
    "tmp1"."s_state"
)
SELECT
  SUM("store_sales"."ss_net_profit") AS "total_sum",
  "store"."s_state" AS "s_state",
  "store"."s_county" AS "s_county",
  GROUPING("store"."s_state") + GROUPING("store"."s_county") AS "lochierarchy",
  RANK() OVER (
    PARTITION BY GROUPING("store"."s_state") + GROUPING("store"."s_county"), CASE WHEN GROUPING("store"."s_county") = 0 THEN "store"."s_state" END
    ORDER BY SUM("store_sales"."ss_net_profit") DESC
  ) AS "rank_within_parent"
FROM "store_sales_2" AS "store_sales"
JOIN "date_dim" AS "d1"
  ON "d1"."d_date_sk" = "store_sales"."ss_sold_date_sk"
  AND "d1"."d_month_seq" <= 1211
  AND "d1"."d_month_seq" >= 1200
JOIN "store" AS "store"
  ON "store"."s_store_sk" = "store_sales"."ss_store_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."s_state" = "store"."s_state"
WHERE
  NOT "_u_0"."s_state" IS NULL
GROUP BY
  ROLLUP (
    "store"."s_state",
    "store"."s_county"
  )
ORDER BY
  "lochierarchy" DESC,
  CASE WHEN "lochierarchy" = 0 THEN "s_state" END,
  "rank_within_parent"
LIMIT 100;
