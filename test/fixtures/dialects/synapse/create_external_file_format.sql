-- CSV external file format
CREATE EXTERNAL FILE FORMAT QuotedCsvWithHeaderFormat
WITH (
    FORMAT_TYPE = DELIMITEDTEXT,
    FORMAT_OPTIONS (
        FIELD_TERMINATOR = ',',
        STRING_DELIMITER = '"',
        FIRST_ROW = 2
    )
);

-- Parquet external file format
CREATE EXTERNAL FILE FORMAT ParquetFormat
WITH (FORMAT_TYPE = PARQUET);

-- Delta Lake external file format
CREATE EXTERNAL FILE FORMAT DeltaLakeFormat
WITH (FORMAT_TYPE = DELTA);
