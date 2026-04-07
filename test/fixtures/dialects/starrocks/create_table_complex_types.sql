CREATE TABLE test_complex_types (
    id INT,
    arr ARRAY<INT>,
    nested_arr ARRAY<ARRAY<VARCHAR>>,
    m MAP<VARCHAR(64), BIGINT>,
    s STRUCT<name VARCHAR(64), age INT>
) ENGINE = olap
DUPLICATE KEY(id)
DISTRIBUTED BY HASH(id) BUCKETS 4;
