-- https://docs.starrocks.io/docs/table_design/indexes/inverted_index/
CREATE TABLE text_search (
    id BIGINT NOT NULL,
    value VARCHAR(255),
    INDEX gin_english (value) USING GIN ("parser" = "english") COMMENT 'english index'
)
DUPLICATE KEY(id)
DISTRIBUTED BY HASH(id);

CREATE TABLE indexed_values (
    id BIGINT,
    category VARCHAR(255),
    description STRING,
    INDEX category_idx (category) USING BITMAP,
    INDEX description_idx (description) USING NGRAMBF (
        "bloom_filter_fpp" = "0.05",
        "gram_num" = "3",
        "case_sensitive" = "false"
    )
)
DUPLICATE KEY(id)
DISTRIBUTED BY HASH(id);

CREATE TABLE vector_search (
    id BIGINT,
    embedding ARRAY<FLOAT>,
    INDEX vector_idx (embedding) USING VECTOR (
        "index_type" = "hnsw",
        "dim" = "5",
        "metric_type" = "cosine_similarity"
    )
)
DUPLICATE KEY(id)
DISTRIBUTED BY HASH(id);
