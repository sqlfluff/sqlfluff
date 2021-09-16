-- File which fails on templating and lexing errors.
SELECT
    {{ something }} as trailing_space   ,
    3 + FROM SELECT FROM
