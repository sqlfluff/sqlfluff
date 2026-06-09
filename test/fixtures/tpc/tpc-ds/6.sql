--------------------------------------
-- TPC-DS 6
--------------------------------------
SELECT a.ca_state state,
               Count(*)   cnt
FROM   customer_address a,
       customer c,
       store_sales s,
       date_dim d,
       item i
WHERE  a.ca_address_sk = c.c_current_addr_sk
       AND c.c_customer_sk = s.ss_customer_sk
       AND s.ss_sold_date_sk = d.d_date_sk
       AND s.ss_item_sk = i.i_item_sk
       AND d.d_month_seq = (SELECT DISTINCT ( d_month_seq )
                            FROM   date_dim
                            WHERE  d_year = 1998
                                   AND d_moy = 7)
       AND i.i_current_price > 1.2 * (SELECT Avg(j.i_current_price)
                                      FROM   item j
                                      WHERE  j.i_category = i.i_category)
GROUP  BY a.ca_state
HAVING Count(*) >= 10
ORDER  BY cnt
LIMIT 100;
WITH "_u_0" AS (
  SELECT DISTINCT
    "date_dim"."d_month_seq" AS "d_month_seq"
  FROM "date_dim" AS "date_dim"
  WHERE
    "date_dim"."d_moy" = 7 AND "date_dim"."d_year" = 1998
), "_u_1" AS (
  SELECT
    AVG("j"."i_current_price") AS "_col_0",
    "j"."i_category" AS "_u_2"
  FROM "item" AS "j"
  GROUP BY
    "j"."i_category"
)
SELECT
  "a"."ca_state" AS "state",
  COUNT(*) AS "cnt"
FROM "customer_address" AS "a"
JOIN "customer" AS "c"
  ON "a"."ca_address_sk" = "c"."c_current_addr_sk"
JOIN "store_sales" AS "s"
  ON "c"."c_customer_sk" = "s"."ss_customer_sk"
JOIN "date_dim" AS "d"
  ON "d"."d_date_sk" = "s"."ss_sold_date_sk"
JOIN "item" AS "i"
  ON "i"."i_item_sk" = "s"."ss_item_sk"
JOIN "_u_0" AS "_u_0"
  ON "_u_0"."d_month_seq" = "d"."d_month_seq"
LEFT JOIN "_u_1" AS "_u_1"
  ON "_u_1"."_u_2" = "i"."i_category"
WHERE
  "i"."i_current_price" > 1.2 * "_u_1"."_col_0"
GROUP BY
  "a"."ca_state"
HAVING
  COUNT(*) >= 10
ORDER BY
  "cnt"
LIMIT 100;
