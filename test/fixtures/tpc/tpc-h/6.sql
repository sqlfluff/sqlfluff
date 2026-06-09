--------------------------------------
-- TPC-H 6
--------------------------------------
select
        sum(l_extendedprice * l_discount) as revenue
from
        lineitem
where
        CAST(l_shipdate AS DATE) >= date '1994-01-01'
        and CAST(l_shipdate AS DATE) < date '1994-01-01' + interval '1' year
        and l_discount between 0.06 - 0.01 and 0.06 + 0.01
        and l_quantity < 24;
SELECT
  SUM("lineitem"."l_extendedprice" * "lineitem"."l_discount") AS "revenue"
FROM "lineitem" AS "lineitem"
WHERE
  "lineitem"."l_discount" <= 0.07
  AND "lineitem"."l_discount" >= 0.05
  AND "lineitem"."l_quantity" < 24
  AND CAST("lineitem"."l_shipdate" AS DATE) < CAST('1995-01-01' AS DATE)
  AND CAST("lineitem"."l_shipdate" AS DATE) >= CAST('1994-01-01' AS DATE);
