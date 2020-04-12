-- Line 4 of this query has a *contained* indent and a closing bracket which we should test handling of.
SELECT
    user_id
FROM (
    SELECT
        c.user_id AS user_id
    FROM
        c
)