--------------------------------------
-- TPC-H 20
--------------------------------------
select
        s_name,
        s_address
from
        supplier,
        nation
where
        s_suppkey in (
                select
                        ps_suppkey
                from
                        partsupp
                where
                        ps_partkey in (
                                select
                                        p_partkey
                                from
                                        part
                                where
                                        p_name like 'forest%'
                        )
                        and ps_availqty > (
                                select
                                        0.5 * sum(l_quantity)
                                from
                                        lineitem
                                where
                                        l_partkey = ps_partkey
                                        and l_suppkey = ps_suppkey
                                        and CAST(l_shipdate AS DATE) >= date '1994-01-01'
                                        and CAST(l_shipdate AS DATE) < date '1994-01-01' + interval '1' year
                        )
        )
        and s_nationkey = n_nationkey
        and n_name = 'CANADA'
order by
        s_name;
WITH "_u_0" AS (
  SELECT
    "part"."p_partkey" AS "p_partkey"
  FROM "part" AS "part"
  WHERE
    "part"."p_name" LIKE 'forest%'
  GROUP BY
    "part"."p_partkey"
), "_u_1" AS (
  SELECT
    0.5 * SUM("lineitem"."l_quantity") AS "_col_0",
    "lineitem"."l_partkey" AS "_u_2",
    "lineitem"."l_suppkey" AS "_u_3"
  FROM "lineitem" AS "lineitem"
  WHERE
    CAST("lineitem"."l_shipdate" AS DATE) < CAST('1995-01-01' AS DATE)
    AND CAST("lineitem"."l_shipdate" AS DATE) >= CAST('1994-01-01' AS DATE)
  GROUP BY
    "lineitem"."l_partkey",
    "lineitem"."l_suppkey"
), "_u_4" AS (
  SELECT
    "partsupp"."ps_suppkey" AS "ps_suppkey"
  FROM "partsupp" AS "partsupp"
  LEFT JOIN "_u_0" AS "_u_0"
    ON "_u_0"."p_partkey" = "partsupp"."ps_partkey"
  LEFT JOIN "_u_1" AS "_u_1"
    ON "_u_1"."_u_2" = "partsupp"."ps_partkey"
    AND "_u_1"."_u_3" = "partsupp"."ps_suppkey"
  WHERE
    "_u_1"."_col_0" < "partsupp"."ps_availqty" AND NOT "_u_0"."p_partkey" IS NULL
  GROUP BY
    "partsupp"."ps_suppkey"
)
SELECT
  "supplier"."s_name" AS "s_name",
  "supplier"."s_address" AS "s_address"
FROM "supplier" AS "supplier"
JOIN "nation" AS "nation"
  ON "nation"."n_name" = 'CANADA'
  AND "nation"."n_nationkey" = "supplier"."s_nationkey"
LEFT JOIN "_u_4" AS "_u_4"
  ON "_u_4"."ps_suppkey" = "supplier"."s_suppkey"
WHERE
  NOT "_u_4"."ps_suppkey" IS NULL
ORDER BY
  "s_name";
