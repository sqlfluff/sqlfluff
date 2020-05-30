SELECT
    COALESCE(id, -1) AS id
FROM some_table
GROUP BY COALESCE(id, -1)
