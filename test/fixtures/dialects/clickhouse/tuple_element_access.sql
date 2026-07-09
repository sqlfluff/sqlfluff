SELECT
  tuple(1, 2, 3) AS arr,
  arr.1 AS dsa;

WITH ((('a', 'aa'), 'b'), 'c') AS test
SELECT
    test.1.1.2,
    (test.1).2,
    test.2;

-- Tuple element access on expressions that are not a bare or bracketed
-- column reference: a function call, an array subscript and a tuple literal
-- (https://github.com/sqlfluff/sqlfluff/issues/8032).
SELECT
    f(x).2,
    arr[1].2,
    (a, b).1,
    f(x).1.2
FROM t;
