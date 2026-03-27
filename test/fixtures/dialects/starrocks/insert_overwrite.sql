INSERT OVERWRITE target_table
PARTITION (p20240101)
WITH LABEL target_table_123
SELECT col1
FROM source_table;
