-- https://fiddle.clickhouse.com/f97798c1-5970-4462-98c4-0e0485b162e7
CREATE HYPOTHETICAL PROJECTION uid_proj ON example INDEX user_id TYPE basic WITH SETTINGS (index_granularity = 4096, index_granularity_bytes = 1048576);

CREATE HYPOTHETICAL PROJECTION region_proj ON default.example
(
    SELECT
        region,
        count(user_id)
    WHERE region = 'JP'
    GROUP BY region
)
;

CREATE HYPOTHETICAL PROJECTION IF NOT EXISTS user_proj ON default.example INDEX trimBoth(CAST(user_id, 'Nullable(String)')) TYPE basic WITH SETTINGS (index_granularity = 4096);

CREATE HYPOTHETICAL PROJECTION region_proj_3 ON default.example
(
    SELECT
        region,
        user_id
    WHERE region = 'JP'
    ORDER BY user_id
) WITH SETTINGS (index_granularity = 4096)
;

CREATE HYPOTHETICAL PROJECTION IF NOT EXISTS region_proj_4 ON default.example
(
    SELECT
        region,
        user_id
    WHERE region = 'JP'
    ORDER BY user_id
)
;

CREATE HYPOTHETICAL PROJECTION IF NOT EXISTS region_proj ON example
(
    WITH
        'JP' AS country
    SELECT
        region,
        count(user_id)
    WHERE region = country
    GROUP BY region
)
;

CREATE HYPOTHETICAL PROJECTION IF NOT EXISTS region_proj_3 ON default.example
(
    WITH
        (1 = 1) AS f1,
        CAST('JP', 'String') AS country
    SELECT
        region,
        user_id
    WHERE region = country
    ORDER BY user_id
) WITH SETTINGS (index_granularity = 4096)
;

CREATE HYPOTHETICAL PROJECTION IF NOT EXISTS region_proj_4 ON example
(
    WITH
        1 = 0 AS f1,
        CAST('JP', 'String') AS country
    SELECT
        region,
        user_id
    WHERE region = country
    ORDER BY user_id
)
;

DROP HYPOTHETICAL PROJECTION uid_proj ON example;

DROP HYPOTHETICAL PROJECTION IF EXISTS region_proj ON example;

DROP HYPOTHETICAL PROJECTION user_proj ON default.example;

DROP HYPOTHETICAL PROJECTION IF EXISTS region_proj_3 ON default.example;

DROP ALL HYPOTHETICAL PROJECTIONS;
