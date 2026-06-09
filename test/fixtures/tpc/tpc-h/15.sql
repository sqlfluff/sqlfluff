--------------------------------------
-- TPC-H 15
--------------------------------------
with revenue (supplier_no, total_revenue) as (
        select
                l_suppkey,
                sum(l_extendedprice * (1 - l_discount))
        from
                lineitem
        where
                CAST(l_shipdate AS DATE) >= date '1996-01-01'
                and CAST(l_shipdate AS DATE) < date '1996-01-01' + interval '3' month
        group by
                l_suppkey)
select
        s_suppkey,
        s_name,
        s_address,
        s_phone,
        total_revenue
from
        supplier,
        revenue
where
        s_suppkey = supplier_no
        and total_revenue = (
                select
                        max(total_revenue)
                from
                        revenue
        )
order by
        s_suppkey;
WITH "revenue" AS (
  SELECT
    "lineitem"."l_suppkey" AS "supplier_no",
    SUM("lineitem"."l_extendedprice" * (
      1 - "lineitem"."l_discount"
    )) AS "total_revenue"
  FROM "lineitem" AS "lineitem"
  WHERE
    CAST("lineitem"."l_shipdate" AS DATE) < CAST('1996-04-01' AS DATE)
    AND CAST("lineitem"."l_shipdate" AS DATE) >= CAST('1996-01-01' AS DATE)
  GROUP BY
    "lineitem"."l_suppkey"
), "_u_0" AS (
  SELECT
    MAX("revenue"."total_revenue") AS "_col_0"
  FROM "revenue" AS "revenue"
)
SELECT
  "supplier"."s_suppkey" AS "s_suppkey",
  "supplier"."s_name" AS "s_name",
  "supplier"."s_address" AS "s_address",
  "supplier"."s_phone" AS "s_phone",
  "revenue"."total_revenue" AS "total_revenue"
FROM "supplier" AS "supplier"
JOIN "revenue" AS "revenue"
  ON "revenue"."supplier_no" = "supplier"."s_suppkey"
JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_col_0" = "revenue"."total_revenue"
ORDER BY
  "s_suppkey";
