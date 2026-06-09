--------------------------------------
-- TPC-H 9
--------------------------------------
select
        nation,
        o_year,
        sum(amount) as sum_profit
from
        (
                select
                        n_name as nation,
                        extract(year from cast(o_orderdate as date)) as o_year,
                        l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount
                from
                        part,
                        supplier,
                        lineitem,
                        partsupp,
                        orders,
                        nation
                where
                        s_suppkey = l_suppkey
                        and ps_suppkey = l_suppkey
                        and ps_partkey = l_partkey
                        and p_partkey = l_partkey
                        and o_orderkey = l_orderkey
                        and s_nationkey = n_nationkey
                        and p_name like '%green%'
        ) as profit
group by
        nation,
        o_year
order by
        nation,
        o_year desc;
SELECT
  "nation"."n_name" AS "nation",
  EXTRACT(YEAR FROM CAST("orders"."o_orderdate" AS DATE)) AS "o_year",
  SUM(
    "lineitem"."l_extendedprice" * (
      1 - "lineitem"."l_discount"
    ) - "partsupp"."ps_supplycost" * "lineitem"."l_quantity"
  ) AS "sum_profit"
FROM "part" AS "part"
JOIN "lineitem" AS "lineitem"
  ON "lineitem"."l_partkey" = "part"."p_partkey"
JOIN "orders" AS "orders"
  ON "lineitem"."l_orderkey" = "orders"."o_orderkey"
JOIN "partsupp" AS "partsupp"
  ON "lineitem"."l_partkey" = "partsupp"."ps_partkey"
  AND "lineitem"."l_suppkey" = "partsupp"."ps_suppkey"
JOIN "supplier" AS "supplier"
  ON "lineitem"."l_suppkey" = "supplier"."s_suppkey"
JOIN "nation" AS "nation"
  ON "nation"."n_nationkey" = "supplier"."s_nationkey"
WHERE
  "part"."p_name" LIKE '%green%'
GROUP BY
  "nation"."n_name",
  EXTRACT(YEAR FROM CAST("orders"."o_orderdate" AS DATE))
ORDER BY
  "nation",
  "o_year" DESC;
