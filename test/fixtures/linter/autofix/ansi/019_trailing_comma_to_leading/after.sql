WITH first_cte AS
(SELECT
    id
    , one
    FROM first)

, second_cte AS
(SELECT
    id
    , two
    FROM {{ source('schema', 'table') }} )

SELECT
    id
    , one
    , two
FROM first_cte
LEFT JOIN second_cte
    ON first_cte.id = second_cte.id;
