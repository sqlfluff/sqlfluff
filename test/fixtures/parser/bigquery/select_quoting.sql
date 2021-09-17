SELECT
    user_id,
    "some string" as list_id
FROM
    `database.schema.benchmark_user_map`
WHERE
    list_id IS NULL
    OR user_id IS NULL