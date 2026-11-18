-- EXPORT DATABASE
EXPORT DATABASE 'target_directory';

-- EXPORT DATABASE with COPY options
EXPORT DATABASE 'target_directory' (FORMAT csv, DELIMITER '|');
EXPORT DATABASE 'target_directory' (FORMAT parquet);
EXPORT DATABASE 'target_directory' (
    FORMAT parquet,
    COMPRESSION zstd,
    ROW_GROUP_SIZE 100_000
);
EXPORT DATABASE 'target_directory' (FORMAT parquet, CODEC 'snappy');

-- IMPORT DATABASE
IMPORT DATABASE 'source_directory';

-- EXPORT DATABASE naming the database to export
EXPORT DATABASE db1 TO 'target_directory';
EXPORT DATABASE "my db" TO 'target_directory' (FORMAT parquet);
