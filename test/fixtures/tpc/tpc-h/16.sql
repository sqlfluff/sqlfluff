--------------------------------------
-- TPC-H 16
--------------------------------------
select
        p_brand,
        p_type,
        p_size,
        count(distinct ps_suppkey) as supplier_cnt
from
        partsupp,
        part
where
        p_partkey = ps_partkey
        and p_brand <> 'Brand#45'
        and p_type not like 'MEDIUM POLISHED%'
        and p_size in (49, 14, 23, 45, 19, 3, 36, 9)
        and ps_suppkey not in (
                select
                        s_suppkey
                from
                        supplier
                where
                        s_comment like '%Customer%Complaints%'
        )
group by
        p_brand,
        p_type,
        p_size
order by
        supplier_cnt desc,
        p_brand,
        p_type,
        p_size;
SELECT
  "part"."p_brand" AS "p_brand",
  "part"."p_type" AS "p_type",
  "part"."p_size" AS "p_size",
  COUNT(DISTINCT "partsupp"."ps_suppkey") AS "supplier_cnt"
FROM "partsupp" AS "partsupp"
JOIN "part" AS "part"
  ON "part"."p_brand" <> 'Brand#45'
  AND "part"."p_partkey" = "partsupp"."ps_partkey"
  AND "part"."p_size" IN (49, 14, 23, 45, 19, 3, 36, 9)
  AND "part"."p_type" NOT LIKE 'MEDIUM POLISHED%'
WHERE
  NOT "partsupp"."ps_suppkey" IN (
    SELECT
      "supplier"."s_suppkey" AS "s_suppkey"
    FROM "supplier" AS "supplier"
    WHERE
      "supplier"."s_comment" LIKE '%Customer%Complaints%'
  )
GROUP BY
  "part"."p_brand",
  "part"."p_type",
  "part"."p_size"
ORDER BY
  "supplier_cnt" DESC,
  "p_brand",
  "p_type",
  "p_size";
