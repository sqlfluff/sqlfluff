--------------------------------------
-- TPC-H 7
--------------------------------------
select
        supp_nation,
        cust_nation,
        l_year,
        sum(volume) as revenue
from
        (
                select
                        n1.n_name as supp_nation,
                        n2.n_name as cust_nation,
                        extract(year from cast(l_shipdate as date)) as l_year,
                        l_extendedprice * (1 - l_discount) as volume
                from
                        supplier,
                        lineitem,
                        orders,
                        customer,
                        nation n1,
                        nation n2
                where
                        s_suppkey = l_suppkey
                        and o_orderkey = l_orderkey
                        and c_custkey = o_custkey
                        and s_nationkey = n1.n_nationkey
                        and c_nationkey = n2.n_nationkey
                        and (
                                (n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY')
                                or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE')
                        )
                        and CAST(l_shipdate AS DATE) between date '1995-01-01' and date '1996-12-31'
        ) as shipping
group by
        supp_nation,
        cust_nation,
        l_year
order by
        supp_nation,
        cust_nation,
        l_year;
SELECT
  "n1"."n_name" AS "supp_nation",
  "n2"."n_name" AS "cust_nation",
  EXTRACT(YEAR FROM CAST("lineitem"."l_shipdate" AS DATE)) AS "l_year",
  SUM("lineitem"."l_extendedprice" * (
    1 - "lineitem"."l_discount"
  )) AS "revenue"
FROM "supplier" AS "supplier"
JOIN "lineitem" AS "lineitem"
  ON "lineitem"."l_suppkey" = "supplier"."s_suppkey"
  AND CAST("lineitem"."l_shipdate" AS DATE) <= CAST('1996-12-31' AS DATE)
  AND CAST("lineitem"."l_shipdate" AS DATE) >= CAST('1995-01-01' AS DATE)
JOIN "nation" AS "n1"
  ON (
    "n1"."n_name" = 'FRANCE' OR "n1"."n_name" = 'GERMANY'
  )
  AND "n1"."n_nationkey" = "supplier"."s_nationkey"
JOIN "orders" AS "orders"
  ON "lineitem"."l_orderkey" = "orders"."o_orderkey"
JOIN "customer" AS "customer"
  ON "customer"."c_custkey" = "orders"."o_custkey"
JOIN "nation" AS "n2"
  ON "customer"."c_nationkey" = "n2"."n_nationkey"
  AND (
    "n1"."n_name" = 'FRANCE' OR "n2"."n_name" = 'FRANCE'
  )
  AND (
    "n1"."n_name" = 'GERMANY' OR "n2"."n_name" = 'GERMANY'
  )
  AND (
    "n2"."n_name" = 'FRANCE' OR "n2"."n_name" = 'GERMANY'
  )
GROUP BY
  "n1"."n_name",
  "n2"."n_name",
  EXTRACT(YEAR FROM CAST("lineitem"."l_shipdate" AS DATE))
ORDER BY
  "supp_nation",
  "cust_nation",
  "l_year";
