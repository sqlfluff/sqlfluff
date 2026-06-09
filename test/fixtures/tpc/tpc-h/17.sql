--------------------------------------
-- TPC-H 17
--------------------------------------
select
        sum(l_extendedprice) / 7.0 as avg_yearly
from
        lineitem,
        part
where
        p_partkey = l_partkey
        and p_brand = 'Brand#23'
        and p_container = 'MED BOX'
        and l_quantity < (
                select
                        0.2 * avg(l_quantity)
                from
                        lineitem
                where
                        l_partkey = p_partkey
        );
WITH "_u_0" AS (
  SELECT
    0.2 * AVG("lineitem"."l_quantity") AS "_col_0",
    "lineitem"."l_partkey" AS "_u_1"
  FROM "lineitem" AS "lineitem"
  GROUP BY
    "lineitem"."l_partkey"
)
SELECT
  SUM("lineitem"."l_extendedprice") / 7.0 AS "avg_yearly"
FROM "lineitem" AS "lineitem"
JOIN "part" AS "part"
  ON "lineitem"."l_partkey" = "part"."p_partkey"
  AND "part"."p_brand" = 'Brand#23'
  AND "part"."p_container" = 'MED BOX'
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "part"."p_partkey"
WHERE
  "_u_0"."_col_0" > "lineitem"."l_quantity";
