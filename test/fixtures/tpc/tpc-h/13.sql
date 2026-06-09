--------------------------------------
-- TPC-H 13
--------------------------------------
select
        c_count,
        count(*) as custdist
from
        (
                select
                        c_custkey,
                        count(o_orderkey)
                from
                        customer left outer join orders on
                                c_custkey = o_custkey
                                and o_comment not like '%special%requests%'
                group by
                        c_custkey
        ) as c_orders (c_custkey, c_count)
group by
        c_count
order by
        custdist desc,
        c_count desc;
WITH "orders_2" AS (
  SELECT
    "orders"."o_orderkey" AS "o_orderkey",
    "orders"."o_custkey" AS "o_custkey",
    "orders"."o_comment" AS "o_comment"
  FROM "orders" AS "orders"
  WHERE
    "orders"."o_comment" NOT LIKE '%special%requests%'
), "c_orders" AS (
  SELECT
    COUNT("orders"."o_orderkey") AS "c_count"
  FROM "customer" AS "customer"
  LEFT JOIN "orders_2" AS "orders"
    ON "customer"."c_custkey" = "orders"."o_custkey"
  GROUP BY
    "customer"."c_custkey"
)
SELECT
  "c_orders"."c_count" AS "c_count",
  COUNT(*) AS "custdist"
FROM "c_orders" AS "c_orders"
GROUP BY
  "c_orders"."c_count"
ORDER BY
  "custdist" DESC,
  "c_count" DESC;
