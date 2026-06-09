--------------------------------------
-- TPC-H 1
--------------------------------------
select
        l_returnflag,
        l_linestatus,
        sum(l_quantity) as sum_qty,
        sum(l_extendedprice) as sum_base_price,
        sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
        sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
        avg(l_quantity) as avg_qty,
        avg(l_extendedprice) as avg_price,
        avg(l_discount) as avg_disc,
        count(*) as count_order
from
        lineitem
where
        CAST(l_shipdate AS DATE) <= date '1998-12-01' - interval '90' day
group by
        l_returnflag,
        l_linestatus
order by
        l_returnflag,
        l_linestatus;
SELECT
  "lineitem"."l_returnflag" AS "l_returnflag",
  "lineitem"."l_linestatus" AS "l_linestatus",
  SUM("lineitem"."l_quantity") AS "sum_qty",
  SUM("lineitem"."l_extendedprice") AS "sum_base_price",
  SUM("lineitem"."l_extendedprice" * (
    1 - "lineitem"."l_discount"
  )) AS "sum_disc_price",
  SUM(
    "lineitem"."l_extendedprice" * (
      1 - "lineitem"."l_discount"
    ) * (
      1 + "lineitem"."l_tax"
    )
  ) AS "sum_charge",
  AVG("lineitem"."l_quantity") AS "avg_qty",
  AVG("lineitem"."l_extendedprice") AS "avg_price",
  AVG("lineitem"."l_discount") AS "avg_disc",
  COUNT(*) AS "count_order"
FROM "lineitem" AS "lineitem"
WHERE
  CAST("lineitem"."l_shipdate" AS DATE) <= CAST('1998-09-02' AS DATE)
GROUP BY
  "lineitem"."l_returnflag",
  "lineitem"."l_linestatus"
ORDER BY
  "l_returnflag",
  "l_linestatus";
