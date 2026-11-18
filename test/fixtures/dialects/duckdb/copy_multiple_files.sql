-- One file per thread, enabled implicitly or explicitly.
COPY (SELECT 42 AS value) TO 'output' (FORMAT PARQUET, PER_THREAD_OUTPUT);
COPY data TO 'output' WITH (FORMAT CSV, PER_THREAD_OUTPUT TRUE);
COPY data TO 'output.csv' (PER_THREAD_OUTPUT FALSE);
COPY data TO 'output' (FORMAT PARQUET, PER_THREAD_OUTPUT 1);
COPY data TO 'output.csv' (PER_THREAD_OUTPUT 0);
COPY data TO 'output' (FORMAT PARQUET, PER_THREAD_OUTPUT 'true');

-- File size limits accept byte counts and human-readable sizes.
COPY data TO 'output' (FORMAT PARQUET, FILE_SIZE_BYTES 1000);
COPY data TO 'output' WITH (FORMAT PARQUET, FILE_SIZE_BYTES '1MB');

-- The options can be combined with existing export options.
COPY (SELECT 42 AS value) TO 'output' (
    FORMAT PARQUET,
    PER_THREAD_OUTPUT TRUE,
    FILE_SIZE_BYTES '1MB',
    COMPRESSION ZSTD
);

-- The new keywords remain valid unquoted column names.
SELECT per_thread_output, file_size_bytes FROM data;
