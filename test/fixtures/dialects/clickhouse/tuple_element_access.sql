SELECT
  tuple(1, 2, 3) AS arr,
  arr.1 AS dsa;

WITH ((('a', 'aa'), 'b'), 'c') AS test
SELECT
    test.1.1.2,
    (test.1).2,
    test.2;
