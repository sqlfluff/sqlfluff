--------------------------------------
-- TPC-H 18
--------------------------------------
select
        c_name,
        c_custkey,
        o_orderkey,
        o_orderdate,
        o_totalprice,
        sum(l_quantity) total_quantity
from
        customer,
        orders,
        lineitem
where
        o_orderkey in (
                select
                        l_orderkey
                from
                        lineitem
                group by
                        l_orderkey having
                                sum(l_quantity) > 300
        )
        and c_custkey = o_custkey
        and o_orderkey = l_orderkey
group by
        c_name,
        c_custkey,
        o_orderkey,
        o_orderdate,
        o_totalprice
order by
        o_totalprice desc,
        o_orderdate
limit
        100;
WITH "_u_0" AS (
  SELECT
    "lineitem"."l_orderkey" AS "l_orderkey"
  FROM "lineitem" AS "lineitem"
  GROUP BY
    "lineitem"."l_orderkey"
  HAVING
    SUM("lineitem"."l_quantity") > 300
)
SELECT
  "customer"."c_name" AS "c_name",
  "customer"."c_custkey" AS "c_custkey",
  "orders"."o_orderkey" AS "o_orderkey",
  "orders"."o_orderdate" AS "o_orderdate",
  "orders"."o_totalprice" AS "o_totalprice",
  SUM("lineitem"."l_quantity") AS "total_quantity"
FROM "customer" AS "customer"
JOIN "orders" AS "orders"
  ON "customer"."c_custkey" = "orders"."o_custkey"
JOIN "lineitem" AS "lineitem"
  ON "lineitem"."l_orderkey" = "orders"."o_orderkey"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."l_orderkey" = "orders"."o_orderkey"
WHERE
  NOT "_u_0"."l_orderkey" IS NULL
GROUP BY
  "customer"."c_name",
  "customer"."c_custkey",
  "orders"."o_orderkey",
  "orders"."o_orderdate",
  "orders"."o_totalprice"
ORDER BY
  "o_totalprice" DESC,
  "o_orderdate"
LIMIT 100;
