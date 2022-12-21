WITH txt AS (
    VALUES (1)
    AS t (id)
)
SELECT *
FROM txt;

WITH txt AS (
    VALUES (1, 2), (3, 4)
    AS t (c1, c2)
)
SELECT *
FROM txt;

SELECT *
FROM (
    VALUES (1)
) AS t(id);

SELECT *
FROM (
    VALUES (1, 2), (3, 4)
) AS t(c1, c2);
