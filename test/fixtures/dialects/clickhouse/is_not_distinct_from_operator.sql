-- https://fiddle.clickhouse.com/0f335e8c-5c00-4222-bc97-d27ce2b3b2c4
SELECT
    a < b AS f1,
    a > b AS f2,
    a <= b AS f3,
    a = b AS f4,
    a == b AS f5,
    a >= b AS f6,
    a <> b AS f7,
    a <=> b AS f8,
    NOT a <=> b AS f9,
    a IS DISTINCT FROM b as f10,
    a IS NOT DISTINCT FROM b as f11
FROM (
    SELECT
        NULL as a,
        NULL as b
)
;
