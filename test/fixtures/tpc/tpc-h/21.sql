--------------------------------------
-- TPC-H 21
--------------------------------------
select
        s_name,
        count(*) as numwait
from
        supplier,
        lineitem l1,
        orders,
        nation
where
        s_suppkey = l1.l_suppkey
        and o_orderkey = l1.l_orderkey
        and o_orderstatus = 'F'
        and l1.l_receiptdate > l1.l_commitdate
        and exists (
                select
                        *
                from
                        lineitem l2
                where
                        l2.l_orderkey = l1.l_orderkey
                        and l2.l_suppkey <> l1.l_suppkey
        )
        and not exists (
                select
                        *
                from
                        lineitem l3
                where
                        l3.l_orderkey = l1.l_orderkey
                        and l3.l_suppkey <> l1.l_suppkey
                        and l3.l_receiptdate > l3.l_commitdate
        )
        and s_nationkey = n_nationkey
        and n_name = 'SAUDI ARABIA'
group by
        s_name
order by
        numwait desc,
        s_name
limit
        100;
WITH "_u_0" AS (
  SELECT
    "l2"."l_orderkey" AS "l_orderkey",
    ARRAY_AGG("l2"."l_suppkey") AS "_u_1"
  FROM "lineitem" AS "l2"
  GROUP BY
    "l2"."l_orderkey"
), "_u_2" AS (
  SELECT
    "l3"."l_orderkey" AS "l_orderkey",
    ARRAY_AGG("l3"."l_suppkey") AS "_u_3"
  FROM "lineitem" AS "l3"
  WHERE
    "l3"."l_commitdate" < "l3"."l_receiptdate"
  GROUP BY
    "l3"."l_orderkey"
)
SELECT
  "supplier"."s_name" AS "s_name",
  COUNT(*) AS "numwait"
FROM "supplier" AS "supplier"
JOIN "lineitem" AS "l1"
  ON "l1"."l_commitdate" < "l1"."l_receiptdate"
  AND "l1"."l_suppkey" = "supplier"."s_suppkey"
JOIN "orders" AS "orders"
  ON "l1"."l_orderkey" = "orders"."o_orderkey" AND "orders"."o_orderstatus" = 'F'
JOIN "nation" AS "nation"
  ON "nation"."n_name" = 'SAUDI ARABIA'
  AND "nation"."n_nationkey" = "supplier"."s_nationkey"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."l_orderkey" = "l1"."l_orderkey"
LEFT JOIN "_u_2" AS "_u_2"
  ON "_u_2"."l_orderkey" = "l1"."l_orderkey"
WHERE
  (
    "_u_2"."l_orderkey" IS NULL
    OR NOT ARRAY_ANY("_u_2"."_u_3", "_x" -> "l1"."l_suppkey" <> "_x")
  )
  AND ARRAY_ANY("_u_0"."_u_1", "_x" -> "l1"."l_suppkey" <> "_x")
  AND NOT "_u_0"."l_orderkey" IS NULL
GROUP BY
  "supplier"."s_name"
ORDER BY
  "numwait" DESC,
  "s_name"
LIMIT 100;
