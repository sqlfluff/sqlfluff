--------------------------------------
-- TPC-DS 1
--------------------------------------
WITH customer_total_return
     AS (SELECT sr_customer_sk     AS ctr_customer_sk,
                sr_store_sk        AS ctr_store_sk,
                Sum(sr_return_amt) AS ctr_total_return
         FROM   store_returns,
                date_dim
         WHERE  sr_returned_date_sk = d_date_sk
                AND d_year = 2001
         GROUP  BY sr_customer_sk,
                   sr_store_sk)
SELECT c_customer_id
FROM   customer_total_return ctr1,
       store,
       customer
WHERE  ctr1.ctr_total_return > (SELECT Avg(ctr_total_return) * 1.2
                                FROM   customer_total_return ctr2
                                WHERE  ctr1.ctr_store_sk = ctr2.ctr_store_sk)
       AND s_store_sk = ctr1.ctr_store_sk
       AND s_state = 'TN'
       AND ctr1.ctr_customer_sk = c_customer_sk
ORDER  BY c_customer_id
LIMIT 100;
WITH "customer_total_return" AS (
  SELECT
    "store_returns"."sr_customer_sk" AS "ctr_customer_sk",
    "store_returns"."sr_store_sk" AS "ctr_store_sk",
    SUM("store_returns"."sr_return_amt") AS "ctr_total_return"
  FROM "store_returns" AS "store_returns"
  JOIN "date_dim" AS "date_dim"
    ON "date_dim"."d_date_sk" = "store_returns"."sr_returned_date_sk"
    AND "date_dim"."d_year" = 2001
  GROUP BY
    "store_returns"."sr_customer_sk",
    "store_returns"."sr_store_sk"
), "_u_0" AS (
  SELECT
    AVG("ctr2"."ctr_total_return") * 1.2 AS "_col_0",
    "ctr2"."ctr_store_sk" AS "_u_1"
  FROM "customer_total_return" AS "ctr2"
  GROUP BY
    "ctr2"."ctr_store_sk"
)
SELECT
  "customer"."c_customer_id" AS "c_customer_id"
FROM "customer_total_return" AS "ctr1"
JOIN "store" AS "store"
  ON "ctr1"."ctr_store_sk" = "store"."s_store_sk" AND "store"."s_state" = 'TN'
JOIN "customer" AS "customer"
  ON "ctr1"."ctr_customer_sk" = "customer"."c_customer_sk"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "ctr1"."ctr_store_sk"
WHERE
  "_u_0"."_col_0" < "ctr1"."ctr_total_return"
ORDER BY
  "c_customer_id"
LIMIT 100;
