-- https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-streaming-table
-- CREATE [ OR REFRESH ] [ PRIVATE ] STREAMING TABLE table_name

CREATE OR REFRESH PRIVATE STREAMING TABLE st_private (
    a BIGINT,
    b STRING
);

CREATE PRIVATE STREAMING TABLE st_private_2 (
    a BIGINT
);

CREATE OR REFRESH PRIVATE STREAMING TABLE st_private_3
AS SELECT
    a,
    b
FROM STREAM(source_table);
