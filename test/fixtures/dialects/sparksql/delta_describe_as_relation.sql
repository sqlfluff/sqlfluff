-- The Delta introspection statements double as relations.
-- https://docs.databricks.com/aws/en/delta/history
SELECT *
FROM (DESCRIBE HISTORY my_table);

SELECT *
FROM (DESCRIBE DETAIL my_table);

SELECT
    version,
    operationMetrics.numAddedFiles AS files_added
FROM (DESCRIBE HISTORY my_table)
WHERE operation = 'OPTIMIZE'
ORDER BY version DESC;

SELECT h.version
FROM (DESCRIBE HISTORY my_table) AS h;

SELECT location
FROM (DESCRIBE DETAIL delta.`/data/events`);

SELECT *
FROM (DESCRIBE HISTORY my_table LIMIT 1);

SELECT 'bronze' AS table_name, location
FROM (DESCRIBE DETAIL main.bronze.raw_tags)
UNION ALL
SELECT 'silver' AS table_name, location
FROM (DESCRIBE DETAIL main.silver.parsed_tags);
