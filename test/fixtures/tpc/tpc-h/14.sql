--------------------------------------
-- TPC-H 14
--------------------------------------
select
        100.00 * sum(case
                when p_type like 'PROMO%'
                        then l_extendedprice * (1 - l_discount)
                else 0
        end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue
from
        lineitem,
        part
where
        l_partkey = p_partkey
        and CAST(l_shipdate AS DATE) >= date '1995-09-01'
        and CAST(l_shipdate AS DATE) < date '1995-09-01' + interval '1' month;
SELECT
  100.00 * SUM(
    CASE
      WHEN "part"."p_type" LIKE 'PROMO%'
      THEN "lineitem"."l_extendedprice" * (
        1 - "lineitem"."l_discount"
      )
      ELSE 0
    END
  ) / SUM("lineitem"."l_extendedprice" * (
    1 - "lineitem"."l_discount"
  )) AS "promo_revenue"
FROM "lineitem" AS "lineitem"
JOIN "part" AS "part"
  ON "lineitem"."l_partkey" = "part"."p_partkey"
WHERE
  CAST("lineitem"."l_shipdate" AS DATE) < CAST('1995-10-01' AS DATE)
  AND CAST("lineitem"."l_shipdate" AS DATE) >= CAST('1995-09-01' AS DATE);
