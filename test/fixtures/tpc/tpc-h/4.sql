--------------------------------------
-- TPC-H 4
--------------------------------------
select
        o_orderpriority,
        count(*) as order_count
from
        orders
where
        CAST(o_orderdate AS DATE) >= date '1993-07-01'
        and CAST(o_orderdate AS DATE) < date '1993-07-01' + interval '3' month
        and exists (
                select
                        *
                from
                        lineitem
                where
                        l_orderkey = o_orderkey
                        and l_commitdate < l_receiptdate
        )
group by
        o_orderpriority
order by
        o_orderpriority;
WITH "_u_0" AS (
  SELECT
    "lineitem"."l_orderkey" AS "l_orderkey"
  FROM "lineitem" AS "lineitem"
  WHERE
    "lineitem"."l_commitdate" < "lineitem"."l_receiptdate"
  GROUP BY
    "lineitem"."l_orderkey"
)
SELECT
  "orders"."o_orderpriority" AS "o_orderpriority",
  COUNT(*) AS "order_count"
FROM "orders" AS "orders"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."l_orderkey" = "orders"."o_orderkey"
WHERE
  CAST("orders"."o_orderdate" AS DATE) < CAST('1993-10-01' AS DATE)
  AND CAST("orders"."o_orderdate" AS DATE) >= CAST('1993-07-01' AS DATE)
  AND NOT "_u_0"."l_orderkey" IS NULL
GROUP BY
  "orders"."o_orderpriority"
ORDER BY
  "o_orderpriority";
