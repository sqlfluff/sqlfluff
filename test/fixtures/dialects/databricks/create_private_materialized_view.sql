CREATE PRIVATE MATERIALIZED VIEW dlt_private_mat_view (
    a STRING COMMENT 'a',
    b TIMESTAMP COMMENT 'b'
)
COMMENT 'DLT private materialized view'
AS SELECT
    a,
    b
FROM live.dlt_bronze;

CREATE OR REFRESH PRIVATE MATERIALIZED VIEW dlt_refresh_private_mat_view (
    a STRING COMMENT 'a',
    b TIMESTAMP COMMENT 'b'
)
COMMENT 'DLT refreshed private materialized view'
AS SELECT
    a,
    b
FROM live.dlt_bronze;
