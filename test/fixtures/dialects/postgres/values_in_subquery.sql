WITH t (col_1, col_2) AS (
    VALUES
    ('08RIX0', 0.435::NUMERIC(4, 3))
)

SELECT *
FROM t;

SELECT *
FROM (
    VALUES (1)
) AS t(c1);

SELECT *
FROM (
    VALUES (1, 2), (3, 4)
) AS t(c1, c2);
