--noqa: disable=ST06
SELECT DISTINCT
    TO_CHAR(a, 'YYYY-MM-dd HH:MM:ss') as the_date,
    a AS b
FROM
    table1;

SELECT
    col_a a,
    col_b b, --noqa: disable=AL02
    col_c c,
    col_d d, --noqa: enable=AL02
    col_e e,
    col_f f,
    col_g g,  --noqa
    col_h h,
    col_i i, --noqa:AL02
    col_j j,
    col_k k, --noqa:AL03
    col_l l,
    col_m m,
    col_n n, --noqa: disable=all
    col_o o,
    col_p p --noqa: enable=all
FROM foo
