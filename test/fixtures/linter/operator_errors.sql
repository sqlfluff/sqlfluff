SELECT
    a.a + a.b as good,
    a.a  - a.b as bad_1,
    a.a *  a.b as bad_2,
    a.b /
    a.a as bad_3,
    a.b
    and a.a as good_4
FROM tbl as a
