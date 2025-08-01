-- Test AggregateFunction data type

CREATE TABLE test_aggregate_function
(
    id UInt64,
    user_count AggregateFunction(count, UInt64),
    sum_values AggregateFunction(sum, Decimal(10, 2)),
    avg_score AggregateFunction(avg, Float64),
    unique_users AggregateFunction(uniq, String),
    quantile_data AggregateFunction(quantile(0.95), Float64)
)
ENGINE = MergeTree()
ORDER BY id;