--------------------------------------
-- TPC-H 12
--------------------------------------
select
        l_shipmode,
        sum(case
                when o_orderpriority = '1-URGENT'
                        or o_orderpriority = '2-HIGH'
                        then 1
                else 0
        end) as high_line_count,
        sum(case
                when o_orderpriority <> '1-URGENT'
                        and o_orderpriority <> '2-HIGH'
                        then 1
                else 0
        end) as low_line_count
from
        orders,
        lineitem
where
        o_orderkey = l_orderkey
        and l_shipmode in ('MAIL', 'SHIP')
        and l_commitdate < l_receiptdate
        and l_shipdate < l_commitdate
        and CAST(l_receiptdate AS DATE) >= date '1994-01-01'
        and CAST(l_receiptdate AS DATE) < date '1994-01-01' + interval '1' year
group by
        l_shipmode
order by
        l_shipmode;
SELECT
  "lineitem"."l_shipmode" AS "l_shipmode",
  SUM(
    CASE
      WHEN "orders"."o_orderpriority" = '1-URGENT' OR "orders"."o_orderpriority" = '2-HIGH'
      THEN 1
      ELSE 0
    END
  ) AS "high_line_count",
  SUM(
    CASE
      WHEN "orders"."o_orderpriority" <> '1-URGENT'
      AND "orders"."o_orderpriority" <> '2-HIGH'
      THEN 1
      ELSE 0
    END
  ) AS "low_line_count"
FROM "orders" AS "orders"
JOIN "lineitem" AS "lineitem"
  ON "lineitem"."l_commitdate" < "lineitem"."l_receiptdate"
  AND "lineitem"."l_commitdate" > "lineitem"."l_shipdate"
  AND "lineitem"."l_orderkey" = "orders"."o_orderkey"
  AND "lineitem"."l_shipmode" IN ('MAIL', 'SHIP')
  AND CAST("lineitem"."l_receiptdate" AS DATE) < CAST('1995-01-01' AS DATE)
  AND CAST("lineitem"."l_receiptdate" AS DATE) >= CAST('1994-01-01' AS DATE)
GROUP BY
  "lineitem"."l_shipmode"
ORDER BY
  "l_shipmode";
