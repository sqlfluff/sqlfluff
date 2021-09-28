SELECT
    a.a + a.b AS good,
    a.a  - a.b AS bad_1,
    a.a *  a.b AS bad_2,
    a.b /
    a.a AS bad_3,
    2+(3+6)+7 AS bad_4,
    a.b
    AND a.a AS good_4
FROM tbl AS a
