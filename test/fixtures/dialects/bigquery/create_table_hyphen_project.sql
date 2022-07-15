CREATE OR REPLACE TABLE project-name.dataset_name.table_name
(
    x INT64 OPTIONS(description="An INTEGER field")
)
PARTITION BY DATE(import_ts);
