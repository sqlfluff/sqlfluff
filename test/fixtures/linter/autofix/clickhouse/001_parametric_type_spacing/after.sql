CREATE TABLE t (
    event_created_at DateTime64(3),
    event_created_at_tz DateTime('UTC'),
    obs_value Decimal(18, 9),
    fixed_str FixedString(16),
    nullable_col Nullable(String),
    lc_col LowCardinality(String),
    arr_col Array(UInt8),
    map_col Map(String, UInt8),
    enum_col Enum8('a' = 1, 'b' = 2),
    tuple_col Tuple(UInt8, String),
    nested_col Nested(a UInt8, b String),
    t64 Time64(3),
    dec32 Decimal32(3),
    dec64 Decimal64(6)
) ENGINE = MergeTree ORDER BY event_created_at;
