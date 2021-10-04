--noqa: disable=L034
SELECT DISTINCT
    TO_CHAR(a, 'YYYY-MM-dd HH:MM:ss') AS the_date,
    a AS b
FROM
    table1;

SELECT
    col_a AS a,
    col_b b, --noqa: disable=L012
    col_c c,
    col_d AS d, --noqa: enable=L012
    col_e AS e,
    col_f AS f,
    col_g g,  --noqa
    col_h AS h,
    col_i i, --noqa:L012
    col_j AS j,
    col_k AS k, --noqa:L013
    col_l AS l,
    col_m AS m,
    col_n n, --noqa: disable=all
    col_o o,
    col_p AS p --noqa: enable=all
FROM foo
