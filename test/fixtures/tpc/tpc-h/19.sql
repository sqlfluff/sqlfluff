--------------------------------------
-- TPC-H 19
--------------------------------------
select
        sum(l_extendedprice* (1 - l_discount)) as revenue
from
        lineitem,
        part
where
        (
                p_partkey = l_partkey
                and p_brand = 'Brand#12'
                and p_container in ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG')
                and l_quantity >= 1 and l_quantity <= 11
                and p_size between 1 and 5
                and l_shipmode in ('AIR', 'AIR REG')
                and l_shipinstruct = 'DELIVER IN PERSON'
        )
        or
        (
                p_partkey = l_partkey
                and p_brand = 'Brand#23'
                and p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
                and l_quantity >= 10 and l_quantity <= 20
                and p_size between 1 and 10
                and l_shipmode in ('AIR', 'AIR REG')
                and l_shipinstruct = 'DELIVER IN PERSON'
        )
        or
        (
                p_partkey = l_partkey
                and p_brand = 'Brand#34'
                and p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
                and l_quantity >= 20 and l_quantity <= 30
                and p_size between 1 and 15
                and l_shipmode in ('AIR', 'AIR REG')
                and l_shipinstruct = 'DELIVER IN PERSON'
        );
SELECT
  SUM("lineitem"."l_extendedprice" * (
    1 - "lineitem"."l_discount"
  )) AS "revenue"
FROM "lineitem" AS "lineitem"
JOIN "part" AS "part"
  ON (
    "lineitem"."l_partkey" = "part"."p_partkey"
    AND "lineitem"."l_quantity" <= 11
    AND "lineitem"."l_quantity" >= 1
    AND "lineitem"."l_shipinstruct" = 'DELIVER IN PERSON'
    AND "lineitem"."l_shipmode" IN ('AIR', 'AIR REG')
    AND "part"."p_brand" = 'Brand#12'
    AND "part"."p_container" IN ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG')
    AND "part"."p_size" <= 5
    AND "part"."p_size" >= 1
  )
  OR (
    "lineitem"."l_partkey" = "part"."p_partkey"
    AND "lineitem"."l_quantity" <= 20
    AND "lineitem"."l_quantity" >= 10
    AND "lineitem"."l_shipinstruct" = 'DELIVER IN PERSON'
    AND "lineitem"."l_shipmode" IN ('AIR', 'AIR REG')
    AND "part"."p_brand" = 'Brand#23'
    AND "part"."p_container" IN ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
    AND "part"."p_size" <= 10
    AND "part"."p_size" >= 1
  )
  OR (
    "lineitem"."l_partkey" = "part"."p_partkey"
    AND "lineitem"."l_quantity" <= 30
    AND "lineitem"."l_quantity" >= 20
    AND "lineitem"."l_shipinstruct" = 'DELIVER IN PERSON'
    AND "lineitem"."l_shipmode" IN ('AIR', 'AIR REG')
    AND "part"."p_brand" = 'Brand#34'
    AND "part"."p_container" IN ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
    AND "part"."p_size" <= 15
    AND "part"."p_size" >= 1
  )
WHERE
  (
    "lineitem"."l_partkey" = "part"."p_partkey"
    AND "lineitem"."l_quantity" <= 11
    AND "lineitem"."l_quantity" >= 1
    AND "lineitem"."l_shipinstruct" = 'DELIVER IN PERSON'
    AND "lineitem"."l_shipmode" IN ('AIR', 'AIR REG')
    AND "part"."p_brand" = 'Brand#12'
    AND "part"."p_container" IN ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG')
    AND "part"."p_size" <= 5
    AND "part"."p_size" >= 1
  )
  OR (
    "lineitem"."l_partkey" = "part"."p_partkey"
    AND "lineitem"."l_quantity" <= 20
    AND "lineitem"."l_quantity" >= 10
    AND "lineitem"."l_shipinstruct" = 'DELIVER IN PERSON'
    AND "lineitem"."l_shipmode" IN ('AIR', 'AIR REG')
    AND "part"."p_brand" = 'Brand#23'
    AND "part"."p_container" IN ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
    AND "part"."p_size" <= 10
    AND "part"."p_size" >= 1
  )
  OR (
    "lineitem"."l_partkey" = "part"."p_partkey"
    AND "lineitem"."l_quantity" <= 30
    AND "lineitem"."l_quantity" >= 20
    AND "lineitem"."l_shipinstruct" = 'DELIVER IN PERSON'
    AND "lineitem"."l_shipmode" IN ('AIR', 'AIR REG')
    AND "part"."p_brand" = 'Brand#34'
    AND "part"."p_container" IN ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
    AND "part"."p_size" <= 15
    AND "part"."p_size" >= 1
  );
