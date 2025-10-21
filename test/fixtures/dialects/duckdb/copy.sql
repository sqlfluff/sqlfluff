-- Basic COPY TO with FORMAT
COPY (SELECT * FROM tbl) TO 'output.parquet' (FORMAT parquet);

-- COPY TO with WITH keyword
COPY (SELECT * FROM tbl) TO 'output.csv' WITH (FORMAT csv);

-- COPY TO with COMPRESSION
COPY (SELECT NOW()) TO 'test.parquet' WITH (FORMAT parquet, COMPRESSION 'snappy');

-- COPY TO with COMPRESSION without quotes
COPY (SELECT * FROM data) TO 'output.parquet' (FORMAT parquet, COMPRESSION gzip);

-- COPY TO with COMPRESSION_LEVEL
COPY (SELECT * FROM data) TO 'compressed.parquet' WITH (
    FORMAT parquet,
    COMPRESSION 'zstd',
    COMPRESSION_LEVEL 9
);

-- COPY TO with ROW_GROUP_SIZE
COPY (SELECT * FROM large_table) TO 'output.parquet' (
    FORMAT parquet,
    ROW_GROUP_SIZE 100000
);

-- COPY TO with PARQUET_VERSION
COPY (SELECT * FROM data) TO 'output.parquet' (
    FORMAT parquet,
    PARQUET_VERSION 'V2'
);

-- COPY TO with PARTITION_BY single column
COPY (SELECT * FROM sales) TO 'partitioned' WITH (
    FORMAT parquet,
    PARTITION_BY year
);

-- COPY TO with PARTITION_BY multiple columns
COPY (SELECT * FROM sales) TO 'partitioned' (
    FORMAT parquet,
    PARTITION_BY (year, month)
);

-- COPY TO with WRITE_PARTITION_COLUMNS
COPY (SELECT * FROM sales) TO 'partitioned' WITH (
    FORMAT parquet,
    PARTITION_BY (year, month),
    WRITE_PARTITION_COLUMNS true
);

-- COPY TO with OVERWRITE
COPY (SELECT * FROM data) TO 'output.parquet' (
    FORMAT parquet,
    OVERWRITE true
);

-- COPY TO with OVERWRITE_OR_IGNORE
COPY (SELECT * FROM data) TO 'output.parquet' WITH (
    FORMAT parquet,
    OVERWRITE_OR_IGNORE true
);

-- COPY TO with APPEND
COPY (SELECT * FROM new_data) TO 'existing.parquet' (
    FORMAT parquet,
    APPEND true
);

-- COPY TO with multiple options
COPY (SELECT * FROM sales) TO 'export.parquet' WITH (
    FORMAT parquet,
    COMPRESSION 'zstd',
    COMPRESSION_LEVEL 3,
    ROW_GROUP_SIZE 50000,
    PARTITION_BY region,
    OVERWRITE true
);

-- COPY TO from table reference
COPY my_table TO 'output.parquet' (FORMAT parquet);

-- COPY TO from table with column list
COPY my_table (col1, col2, col3) TO 'output.csv' WITH (FORMAT csv);

-- COPY FROM basic
COPY my_table FROM 'input.csv' WITH (FORMAT csv, HEADER true);

-- COPY FROM with WHERE clause
COPY my_table FROM 'input.csv' WITH (FORMAT csv) WHERE id > 100;
