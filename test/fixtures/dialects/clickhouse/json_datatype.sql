-- Bare JSON type
CREATE TABLE t1 (c JSON) ENGINE = MergeTree ORDER BY tuple();

-- JSON with dynamic-path / dynamic-type parameters
CREATE TABLE t2 (c JSON(max_dynamic_paths = 16)) ENGINE = MergeTree ORDER BY tuple();

CREATE TABLE t3 (c JSON(max_dynamic_paths = 16, max_dynamic_types = 8)) ENGINE = MergeTree ORDER BY tuple();

-- JSON with typed-path hints, including dotted paths
CREATE TABLE t4 (
    c JSON(some.path UInt32, content_type LowCardinality(String))
) ENGINE = MergeTree ORDER BY tuple();

-- JSON with SKIP and SKIP REGEXP directives
CREATE TABLE t5 (
    c JSON(max_dynamic_paths = 4, a.b UInt32, SKIP a.c, SKIP REGEXP 'paths_to_skip.*')
) ENGINE = MergeTree ORDER BY tuple();

-- JSON column with a default value
CREATE TABLE t6 (
    `ephemeral_detail` JSON(
        max_dynamic_paths = 64,
        content_type LowCardinality(String),
        source LowCardinality(String),
        truncated Bool
    ) DEFAULT '{}'
) ENGINE = MergeTree ORDER BY tuple();
