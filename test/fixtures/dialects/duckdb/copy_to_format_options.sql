-- Parquet options
COPY tbl TO 'parquet_output' (
    FORMAT parquet,
    ROW_GROUPS_PER_FILE 2,
    CHUNK_SIZE 1000,
    DATA_PAGE_SIZE_LIMIT 65536,
    DICTIONARY_SIZE_LIMIT 0,
    WRITE_BLOOM_FILTER false,
    BLOOM_FILTER_FALSE_POSITIVE_RATIO 0.001
);
COPY tbl TO 'output.parquet' (FORMAT parquet, FIELD_IDS {i: 42, j: 43});
COPY tbl TO 'output.parquet' (FORMAT parquet, FIELD_IDS 'auto');
COPY tbl TO 'output.parquet' (FORMAT parquet, FIELD_IDS auto);
COPY tbl TO 'output.parquet' (
    FORMAT parquet, KV_METADATA {origin: 'sqlfluff', version: '1'}
);
COPY variants TO 'output.parquet' (FORMAT parquet, SHREDDING {v: 'INTEGER'});
COPY tbl TO 'output.parquet' (
    FORMAT parquet,
    PARQUET_VERSION V2,
    GEOPARQUET_VERSION 'NONE',
    TIMESTAMP_IS_ADJUSTED_TO_UTC AUTO,
    WRITE_TIMESTAMP_AS_INT96 true
);
COPY tbl TO 'output.parquet' (
    FORMAT parquet,
    PARQUET_VERSION 'V1',
    GEOPARQUET_VERSION V2,
    TIMESTAMP_IS_ADJUSTED_TO_UTC false
);

-- JSON options
COPY tbl TO 'output.json' (FORMAT json, ARRAY true);
COPY tbl TO 'output.json' (FORMAT json, ARRAY);

-- The option names still work as column names
SELECT
    field_ids,
    chunk_size,
    kv_metadata,
    shredding,
    row_groups_per_file
FROM tbl;
