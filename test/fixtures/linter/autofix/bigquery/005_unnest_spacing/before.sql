SELECT
    category,
    value
FROM
    table1,
UNNEST(1, 2, 3) AS category
