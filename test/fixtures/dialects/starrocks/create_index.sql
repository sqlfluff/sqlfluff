CREATE INDEX category_idx ON indexed_values (category) USING BITMAP;

CREATE INDEX gin_english ON text_search (value)
USING GIN ("parser" = "english") COMMENT 'english index';

CREATE INDEX description_idx ON indexed_values (description)
USING NGRAMBF ("bloom_filter_fpp" = "0.05", "gram_num" = "3");

CREATE INDEX vector_idx ON vector_search (embedding)
USING VECTOR ("index_type" = "hnsw", "dim" = "5", "metric_type" = "cosine_similarity");
