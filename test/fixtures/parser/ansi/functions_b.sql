-- Thanks @mrshu for this query, it tests nested functions
SELECT
    SPLIT(LOWER(text1), ' ') AS text1
FROM "database"."sample_table"
