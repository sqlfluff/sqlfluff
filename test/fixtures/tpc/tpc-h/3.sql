--------------------------------------
-- TPC-H 3
--------------------------------------
select
        l_orderkey,
        sum(l_extendedprice * (1 - l_discount)) as revenue,
        CAST(o_orderdate AS STRING) AS o_orderdate,
        o_shippriority
from
        customer,
        orders,
        lineitem
where
        c_mktsegment = 'BUILDING'
        and c_custkey = o_custkey
        and l_orderkey = o_orderkey
        and o_orderdate < '1995-03-15'
        and l_shipdate > '1995-03-15'
group by
        l_orderkey,
        o_orderdate,
        o_shippriority
order by
        revenue desc,
        o_orderdate
limit
        10;
SELECT
  "lineitem"."l_orderkey" AS "l_orderkey",
  SUM("lineitem"."l_extendedprice" * (
    1 - "lineitem"."l_discount"
  )) AS "revenue",
  "orders"."o_orderdate" AS "o_orderdate",
  "orders"."o_shippriority" AS "o_shippriority"
FROM "customer" AS "customer"
JOIN "orders" AS "orders"
  ON "customer"."c_custkey" = "orders"."o_custkey"
  AND "orders"."o_orderdate" < '1995-03-15'
JOIN "lineitem" AS "lineitem"
  ON "lineitem"."l_orderkey" = "orders"."o_orderkey"
  AND "lineitem"."l_shipdate" > '1995-03-15'
WHERE
  "customer"."c_mktsegment" = 'BUILDING'
GROUP BY
  "lineitem"."l_orderkey",
  "orders"."o_orderdate",
  "orders"."o_shippriority"
ORDER BY
  "revenue" DESC,
  "o_orderdate"
LIMIT 10;
