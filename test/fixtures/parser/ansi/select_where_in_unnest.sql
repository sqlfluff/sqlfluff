SELECT
    user_id
FROM
    t
WHERE
    1 IN UNNEST(t.c)
