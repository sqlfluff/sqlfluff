-- https://github.com/sqlfluff/sqlfluff/issues/8110
SELECT
    1.,
    1.0,
    22.50
FROM ex_tab
WHERE ex_col = 1.;
