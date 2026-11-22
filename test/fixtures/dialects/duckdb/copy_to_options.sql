-- Boolean options, with the value given or left out (which means true).
COPY tbl TO 'output.parquet' (FORMAT PARQUET, RETURN_STATS);
COPY tbl TO 'output.parquet' (FORMAT PARQUET, RETURN_FILES TRUE);
COPY tbl TO 'output.csv' (FORMAT CSV, PRESERVE_ORDER FALSE);
COPY tbl TO 'output.csv' WITH (FORMAT CSV, USE_TMP_FILE FALSE);

-- Naming the files written by a partitioned or multi-file copy.
COPY tbl TO 'output' (
    FORMAT CSV,
    PARTITION_BY (part_col),
    FILENAME_PATTERN 'file_{i}',
    FILE_EXTENSION 'txt',
    RETURN_FILES
);
COPY tbl TO 'parquet_output' (
    FORMAT PARQUET,
    PARTITION_BY (part_col),
    FILENAME_PATTERN "file_{uuid}",
    FILE_EXTENSION parq
);

-- The new keywords remain valid unquoted column names.
SELECT
    use_tmp_file,
    preserve_order,
    return_files,
    return_stats,
    filename_pattern,
    file_extension
FROM tbl;
