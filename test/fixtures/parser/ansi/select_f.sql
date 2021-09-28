-- Test the parser on complex maths
SELECT
    COS(2*ACOS(-1)*2*y/53) AS c2
FROM
    t
