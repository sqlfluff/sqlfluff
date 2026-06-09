--------------------------------------
-- TPC-H 11
--------------------------------------
select
        ps_partkey,
        sum(ps_supplycost * ps_availqty) as value
from
        partsupp,
        supplier,
        nation
where
        ps_suppkey = s_suppkey
        and s_nationkey = n_nationkey
        and n_name = 'GERMANY'
group by
        ps_partkey having
                sum(ps_supplycost * ps_availqty) > (
                        select
                                sum(ps_supplycost * ps_availqty) * 0.0001
                        from
                                partsupp,
                                supplier,
                                nation
                        where
                                ps_suppkey = s_suppkey
                                and s_nationkey = n_nationkey
                                and n_name = 'GERMANY'
                )
order by
        value desc;
WITH "supplier_2" AS (
  SELECT
    "supplier"."s_suppkey" AS "s_suppkey",
    "supplier"."s_nationkey" AS "s_nationkey"
  FROM "supplier" AS "supplier"
), "nation_2" AS (
  SELECT
    "nation"."n_nationkey" AS "n_nationkey",
    "nation"."n_name" AS "n_name"
  FROM "nation" AS "nation"
  WHERE
    "nation"."n_name" = 'GERMANY'
), "_u_0" AS (
  SELECT
    SUM("partsupp"."ps_supplycost" * "partsupp"."ps_availqty") * 0.0001 AS "_col_0"
  FROM "partsupp" AS "partsupp"
  JOIN "supplier_2" AS "supplier"
    ON "partsupp"."ps_suppkey" = "supplier"."s_suppkey"
  JOIN "nation_2" AS "nation"
    ON "nation"."n_nationkey" = "supplier"."s_nationkey"
)
SELECT
  "partsupp"."ps_partkey" AS "ps_partkey",
  SUM("partsupp"."ps_supplycost" * "partsupp"."ps_availqty") AS "value"
FROM "partsupp" AS "partsupp"
CROSS JOIN "_u_0" AS "_u_0"
JOIN "supplier_2" AS "supplier"
  ON "partsupp"."ps_suppkey" = "supplier"."s_suppkey"
JOIN "nation_2" AS "nation"
  ON "nation"."n_nationkey" = "supplier"."s_nationkey"
GROUP BY
  "partsupp"."ps_partkey"
HAVING
  MAX("_u_0"."_col_0") < SUM("partsupp"."ps_supplycost" * "partsupp"."ps_availqty")
ORDER BY
  "value" DESC;
