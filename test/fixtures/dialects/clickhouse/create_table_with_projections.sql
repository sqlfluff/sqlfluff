-- Test PROJECTION definitions

CREATE TABLE test_projections
(
    id UInt64,
    name String,
    category String, 
    price Decimal(10, 2),
    created_date Date,
    
    PROJECTION proj_simple
    (
        SELECT category, count(id) GROUP BY category
    )
)
ENGINE = MergeTree()
ORDER BY id;