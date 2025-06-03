-- Taken from examples here: https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files

-- Reads the files available in the given path. Auto-detects the format and schema of the data.
SELECT * FROM read_files('abfss://container@storageAccount.dfs.core.windows.net/base/path');

SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv',
    schema => 'id int, ts timestamp, event string');

-- Infers the schema of CSV files with headers. Because the schema is not provided,
-- the CSV files are assumed to have headers.
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv');

-- Reads files that have a csv suffix.
SELECT * FROM read_files('s3://bucket/path/*.csv');

-- Reads a single JSON file
SELECT * FROM read_files(
    'abfss://container@storageAccount.dfs.core.windows.net/path/single.json');

-- Reads JSON files and overrides the data type of the column `id` to integer.
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int');

-- Reads files that have been uploaded or modified yesterday.
SELECT * FROM read_files(
    'gs://my-bucket/avroData',
    modifiedAfter => date_sub(current_date(), 1),
    modifiedBefore => current_date());

-- Reads a streaming table
SELECT * FROM STREAM read_files('gs://my-bucket/avroData', includeExistingFiles => false);
