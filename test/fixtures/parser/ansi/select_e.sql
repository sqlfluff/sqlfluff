-- Union expressions
SELECT
    col_a as foo
FROM some_table

UNION

SELECT
    col_b as foo
FROM another_table

UNION ALL

SELECT
    col_c as foo
FROM this_other_table

INTERSECT

SELECT
    col_d as foo
FROM the_last_table
