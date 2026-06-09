--------------------------------------
-- TPC-H 2
--------------------------------------
select
   s_acctbal,
   s_name,
   n_name,
   p_partkey,
   p_mfgr,
   s_address,
   s_phone,
   s_comment
from
   part,
   supplier,
   partsupp,
   nation,
   region
where
   p_partkey = ps_partkey
   and s_suppkey = ps_suppkey
   and p_size = 15
   and p_type like '%BRASS'
   and s_nationkey = n_nationkey
   and n_regionkey = r_regionkey
   and r_name = 'EUROPE'
   and ps_supplycost = (
           select
                   min(ps_supplycost)
           from
                   partsupp,
                   supplier,
                   nation,
                   region
           where
                   p_partkey = ps_partkey
                   and s_suppkey = ps_suppkey
                   and s_nationkey = n_nationkey
                   and n_regionkey = r_regionkey
                   and r_name = 'EUROPE'
   )
order by
   s_acctbal desc,
   n_name,
   s_name,
   p_partkey
limit
   100;
WITH "partsupp_2" AS (
  SELECT
    "partsupp"."ps_partkey" AS "ps_partkey",
    "partsupp"."ps_suppkey" AS "ps_suppkey",
    "partsupp"."ps_supplycost" AS "ps_supplycost"
  FROM "partsupp" AS "partsupp"
), "region_2" AS (
  SELECT
    "region"."r_regionkey" AS "r_regionkey",
    "region"."r_name" AS "r_name"
  FROM "region" AS "region"
  WHERE
    "region"."r_name" = 'EUROPE'
), "_u_0" AS (
  SELECT
    MIN("partsupp"."ps_supplycost") AS "_col_0",
    "partsupp"."ps_partkey" AS "_u_1"
  FROM "partsupp_2" AS "partsupp"
  JOIN "supplier" AS "supplier"
    ON "partsupp"."ps_suppkey" = "supplier"."s_suppkey"
  JOIN "nation" AS "nation"
    ON "nation"."n_nationkey" = "supplier"."s_nationkey"
  JOIN "region_2" AS "region"
    ON "nation"."n_regionkey" = "region"."r_regionkey"
  GROUP BY
    "partsupp"."ps_partkey"
)
SELECT
  "supplier"."s_acctbal" AS "s_acctbal",
  "supplier"."s_name" AS "s_name",
  "nation"."n_name" AS "n_name",
  "part"."p_partkey" AS "p_partkey",
  "part"."p_mfgr" AS "p_mfgr",
  "supplier"."s_address" AS "s_address",
  "supplier"."s_phone" AS "s_phone",
  "supplier"."s_comment" AS "s_comment"
FROM "part" AS "part"
CROSS JOIN "supplier" AS "supplier"
JOIN "partsupp_2" AS "partsupp"
  ON "part"."p_partkey" = "partsupp"."ps_partkey"
  AND "partsupp"."ps_suppkey" = "supplier"."s_suppkey"
JOIN "nation" AS "nation"
  ON "nation"."n_nationkey" = "supplier"."s_nationkey"
JOIN "region_2" AS "region"
  ON "nation"."n_regionkey" = "region"."r_regionkey"
LEFT JOIN "_u_0" AS "_u_0"
  ON "_u_0"."_u_1" = "part"."p_partkey"
WHERE
  "_u_0"."_col_0" = "partsupp"."ps_supplycost"
  AND "part"."p_size" = 15
  AND "part"."p_type" LIKE '%BRASS'
ORDER BY
  "s_acctbal" DESC,
  "n_name",
  "s_name",
  "p_partkey"
LIMIT 100;
