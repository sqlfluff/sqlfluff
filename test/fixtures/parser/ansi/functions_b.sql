-- Thanks @mrshu for this query, it tests nested functions
SELECT
    SPLIT(LOWER(text), ' ') AS text
FROM "database"."sample_table"
