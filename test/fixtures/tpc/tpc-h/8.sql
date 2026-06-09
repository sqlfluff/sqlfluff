--------------------------------------
-- TPC-H 8
--------------------------------------
select
        o_year,
        sum(case
                when nation = 'BRAZIL' then volume
                else 0
        end) / sum(volume) as mkt_share
from
        (
                select
                        extract(YEAR from cast(o_orderdate as date)) as o_year,
                        l_extendedprice * (1 - l_discount) as volume,
                        n2.n_name as nation
                from
                        part,
                        supplier,
                        lineitem,
                        orders,
                        customer,
                        nation n1,
                        nation n2,
                        region
                where
                        p_partkey = l_partkey
                        and s_suppkey = l_suppkey
                        and l_orderkey = o_orderkey
                        and o_custkey = c_custkey
                        and c_nationkey = n1.n_nationkey
                        and n1.n_regionkey = r_regionkey
                        and r_name = 'AMERICA'
                        and s_nationkey = n2.n_nationkey
                        and CAST(o_orderdate AS DATE) between date '1995-01-01' and date '1996-12-31'
                        and p_type = 'ECONOMY ANODIZED STEEL'
        ) as all_nations
group by
        o_year
order by
        o_year;
SELECT
  EXTRACT(YEAR FROM CAST("orders"."o_orderdate" AS DATE)) AS "o_year",
  SUM(
    CASE
      WHEN "n2"."n_name" = 'BRAZIL'
      THEN "lineitem"."l_extendedprice" * (
        1 - "lineitem"."l_discount"
      )
      ELSE 0
    END
  ) / SUM("lineitem"."l_extendedprice" * (
    1 - "lineitem"."l_discount"
  )) AS "mkt_share"
FROM "part" AS "part"
JOIN "lineitem" AS "lineitem"
  ON "lineitem"."l_partkey" = "part"."p_partkey"
JOIN "orders" AS "orders"
  ON "lineitem"."l_orderkey" = "orders"."o_orderkey"
  AND CAST("orders"."o_orderdate" AS DATE) <= CAST('1996-12-31' AS DATE)
  AND CAST("orders"."o_orderdate" AS DATE) >= CAST('1995-01-01' AS DATE)
JOIN "supplier" AS "supplier"
  ON "lineitem"."l_suppkey" = "supplier"."s_suppkey"
JOIN "customer" AS "customer"
  ON "customer"."c_custkey" = "orders"."o_custkey"
JOIN "nation" AS "n2"
  ON "n2"."n_nationkey" = "supplier"."s_nationkey"
JOIN "nation" AS "n1"
  ON "customer"."c_nationkey" = "n1"."n_nationkey"
JOIN "region" AS "region"
  ON "n1"."n_regionkey" = "region"."r_regionkey" AND "region"."r_name" = 'AMERICA'
WHERE
  "part"."p_type" = 'ECONOMY ANODIZED STEEL'
GROUP BY
  EXTRACT(YEAR FROM CAST("orders"."o_orderdate" AS DATE))
ORDER BY
  "o_year";
