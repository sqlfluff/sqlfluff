--------------------------------------
-- TPC-H 5
--------------------------------------
select
        n_name,
        sum(l_extendedprice * (1 - l_discount)) as revenue
from
        customer,
        orders,
        lineitem,
        supplier,
        nation,
        region
where
        c_custkey = o_custkey
        and l_orderkey = o_orderkey
        and l_suppkey = s_suppkey
        and c_nationkey = s_nationkey
        and s_nationkey = n_nationkey
        and n_regionkey = r_regionkey
        and r_name = 'ASIA'
        and CAST(o_orderdate AS DATE) >= date '1994-01-01'
        and CAST(o_orderdate AS DATE) < date '1994-01-01' + interval '1' year
group by
        n_name
order by
        revenue desc;
SELECT
  "nation"."n_name" AS "n_name",
  SUM("lineitem"."l_extendedprice" * (
    1 - "lineitem"."l_discount"
  )) AS "revenue"
FROM "customer" AS "customer"
JOIN "orders" AS "orders"
  ON "customer"."c_custkey" = "orders"."o_custkey"
  AND CAST("orders"."o_orderdate" AS DATE) < CAST('1995-01-01' AS DATE)
  AND CAST("orders"."o_orderdate" AS DATE) >= CAST('1994-01-01' AS DATE)
JOIN "lineitem" AS "lineitem"
  ON "lineitem"."l_orderkey" = "orders"."o_orderkey"
JOIN "supplier" AS "supplier"
  ON "customer"."c_nationkey" = "supplier"."s_nationkey"
  AND "lineitem"."l_suppkey" = "supplier"."s_suppkey"
JOIN "nation" AS "nation"
  ON "nation"."n_nationkey" = "supplier"."s_nationkey"
JOIN "region" AS "region"
  ON "nation"."n_regionkey" = "region"."r_regionkey" AND "region"."r_name" = 'ASIA'
GROUP BY
  "nation"."n_name"
ORDER BY
  "revenue" DESC;
