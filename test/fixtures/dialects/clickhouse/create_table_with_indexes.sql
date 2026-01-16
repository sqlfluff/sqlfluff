-- Test all index types we added support for

CREATE TABLE test_indexes
(
    id UInt64,
    name String,
    category LowCardinality(String),
    content String,
    tags Array(String),
    score Float64,
    
    INDEX idx_bloom_filter name TYPE BLOOM_FILTER GRANULARITY 1,
    INDEX idx_bloom_filter_params content TYPE BLOOM_FILTER(0.01) GRANULARITY 1,
    INDEX idx_minmax score TYPE MINMAX GRANULARITY 8192,
    INDEX idx_set category TYPE SET GRANULARITY 100,
    INDEX idx_ngrambf name TYPE NGRAMBF_V1 GRANULARITY 1,
    INDEX idx_tokenbf content TYPE TOKENBF_V1 GRANULARITY 1,
    INDEX idx_hypothesis tags TYPE HYPOTHESIS GRANULARITY 1
)
ENGINE = MergeTree()
ORDER BY id;

-- Test index without parentheses 
CREATE TABLE test_index_simple 
(
    id UInt64,
    name String,
    INDEX idx_simple name TYPE SET GRANULARITY 1
)
ENGINE = MergeTree()
ORDER BY id;

-- Test index with parentheses
CREATE TABLE test_index_bracketed
(
    id UInt64,
    name String,
    category String,
    INDEX idx_bracketed (name, category) TYPE MINMAX GRANULARITY 1
)
ENGINE = MergeTree()
ORDER BY id;
