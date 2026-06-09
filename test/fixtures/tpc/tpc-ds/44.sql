--------------------------------------
-- TPC-DS 44
--------------------------------------
SELECT _ascending.rnk,
               i1.i_product_name best_performing,
               i2.i_product_name worst_performing
FROM  (SELECT *
       FROM   (SELECT item_sk,
                      Rank()
                        OVER (
                          ORDER BY rank_col ASC) rnk
               FROM   (SELECT ss_item_sk         item_sk,
                              Avg(ss_net_profit) rank_col
                       FROM   store_sales ss1
                       WHERE  ss_store_sk = 4
                       GROUP  BY ss_item_sk
                       HAVING Avg(ss_net_profit) > 0.9 *
                              (SELECT Avg(ss_net_profit)
                                      rank_col
                               FROM   store_sales
                               WHERE  ss_store_sk = 4
                                      AND ss_cdemo_sk IS
                                          NULL
                               GROUP  BY ss_store_sk))V1)
              V11
       WHERE  rnk < 11) _ascending,
      (SELECT *
       FROM   (SELECT item_sk,
                      Rank()
                        OVER (
                          ORDER BY rank_col DESC) rnk
               FROM   (SELECT ss_item_sk         item_sk,
                              Avg(ss_net_profit) rank_col
                       FROM   store_sales ss1
                       WHERE  ss_store_sk = 4
                       GROUP  BY ss_item_sk
                       HAVING Avg(ss_net_profit) > 0.9 *
                              (SELECT Avg(ss_net_profit)
                                      rank_col
                               FROM   store_sales
                               WHERE  ss_store_sk = 4
                                      AND ss_cdemo_sk IS
                                          NULL
                               GROUP  BY ss_store_sk))V2)
              V21
       WHERE  rnk < 11) descending,
      item i1,
      item i2
WHERE  _ascending.rnk = descending.rnk
       AND i1.i_item_sk = _ascending.item_sk
       AND i2.i_item_sk = descending.item_sk
ORDER  BY _ascending.rnk
LIMIT 100;
WITH "_u_0" AS (
  SELECT
    AVG("store_sales"."ss_net_profit") AS "rank_col"
  FROM "store_sales" AS "store_sales"
  WHERE
    "store_sales"."ss_cdemo_sk" IS NULL AND "store_sales"."ss_store_sk" = 4
  GROUP BY
    "store_sales"."ss_store_sk"
), "v1" AS (
  SELECT
    "ss1"."ss_item_sk" AS "item_sk",
    AVG("ss1"."ss_net_profit") AS "rank_col"
  FROM "store_sales" AS "ss1"
  CROSS JOIN "_u_0" AS "_u_0"
  WHERE
    "ss1"."ss_store_sk" = 4
  GROUP BY
    "ss1"."ss_item_sk"
  HAVING
    0.9 * MAX("_u_0"."rank_col") < AVG("ss1"."ss_net_profit")
), "v11" AS (
  SELECT
    "v1"."item_sk" AS "item_sk",
    RANK() OVER (ORDER BY "v1"."rank_col") AS "rnk"
  FROM "v1" AS "v1"
), "v2" AS (
  SELECT
    "ss1"."ss_item_sk" AS "item_sk",
    AVG("ss1"."ss_net_profit") AS "rank_col"
  FROM "store_sales" AS "ss1"
  CROSS JOIN "_u_0" AS "_u_1"
  WHERE
    "ss1"."ss_store_sk" = 4
  GROUP BY
    "ss1"."ss_item_sk"
  HAVING
    0.9 * MAX("_u_1"."rank_col") < AVG("ss1"."ss_net_profit")
), "v21" AS (
  SELECT
    "v2"."item_sk" AS "item_sk",
    RANK() OVER (ORDER BY "v2"."rank_col" DESC) AS "rnk"
  FROM "v2" AS "v2"
)
SELECT
  "v11"."rnk" AS "rnk",
  "i1"."i_product_name" AS "best_performing",
  "i2"."i_product_name" AS "worst_performing"
FROM "v11" AS "v11"
JOIN "v21" AS "v21"
  ON "v11"."rnk" = "v21"."rnk" AND "v21"."rnk" < 11
JOIN "item" AS "i1"
  ON "i1"."i_item_sk" = "v11"."item_sk"
JOIN "item" AS "i2"
  ON "i2"."i_item_sk" = "v21"."item_sk"
WHERE
  "v11"."rnk" < 11
ORDER BY
  "v11"."rnk"
LIMIT 100;
