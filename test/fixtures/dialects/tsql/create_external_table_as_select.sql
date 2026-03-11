-- Basic CETAS with minimal options
CREATE EXTERNAL TABLE dbo.MyExternalTable
WITH (
    LOCATION = '/path/to/folder/',
    DATA_SOURCE = my_external_data_source,
    FILE_FORMAT = my_file_format
)
AS SELECT * FROM dbo.SourceTable;

-- CETAS with explicit column list
CREATE EXTERNAL TABLE dbo.MyExternalTable
(
    col1,
    col2,
    col3
)
WITH (
    LOCATION = '/path/to/folder/',
    DATA_SOURCE = my_external_data_source,
    FILE_FORMAT = my_file_format
)
AS SELECT col1, col2, col3 FROM dbo.SourceTable;

-- CETAS with reject options
CREATE EXTERNAL TABLE schema_name.table_name
WITH (
    LOCATION = '/path/to/folder/',
    DATA_SOURCE = external_data_source,
    FILE_FORMAT = parquetfileformat,
    REJECT_TYPE = value,
    REJECT_VALUE = 0
)
AS SELECT * FROM dbo.SourceTable WHERE col1 IS NOT NULL;

-- CETAS with reject sample value
CREATE EXTERNAL TABLE schema_name.table_name
WITH (
    LOCATION = '/path/to/folder/',
    DATA_SOURCE = external_data_source,
    FILE_FORMAT = parquetfileformat,
    REJECT_TYPE = percentage,
    REJECT_VALUE = 5,
    REJECT_SAMPLE_VALUE = 100
)
AS SELECT * FROM dbo.SourceTable;

-- CETAS with a CTE
CREATE EXTERNAL TABLE dbo.Summary
WITH (
    LOCATION = '/summary/',
    DATA_SOURCE = my_external_data_source,
    FILE_FORMAT = my_file_format
)
AS
WITH cte AS (
    SELECT id, SUM(amount) AS total_amount
    FROM dbo.Transactions
    GROUP BY id
)
SELECT * FROM cte;

-- CETAS with three-part table name
CREATE EXTERNAL TABLE database_name.schema_name.table_name
WITH (
    LOCATION = '/output/',
    DATA_SOURCE = my_external_data_source,
    FILE_FORMAT = my_file_format
)
AS SELECT * FROM dbo.SourceTable;
