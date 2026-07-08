SELECT n, source FROM (
   SELECT toFloat32(number % 10) AS n, 'original' AS source
   FROM numbers(10) WHERE number % 3 = 1
) ORDER BY n WITH FILL FROM 0 TO 5.51 STEP 0.5;

SELECT
    toDate((number * 10) * 86400) AS d1,
    toDate(number * 86400) AS d2,
    'original' AS source
FROM numbers(10)
WHERE (number % 3) = 1
ORDER BY
    d2 WITH FILL,
    d1 WITH FILL STEP 5;

SELECT
    toDate((number * 10) * 86400) AS d1,
    toDate(number * 86400) AS d2,
    'original' AS source
FROM numbers(10)
WHERE (number % 3) = 1
ORDER BY
    d1 WITH FILL STEP 5,
    d2 WITH FILL;

SELECT
    toDate((number * 10) * 86400) AS d1,
    toDate(number * 86400) AS d2,
    'original' AS source
FROM numbers(10)
WHERE (number % 3) = 1
ORDER BY
    d1 WITH FILL STEP INTERVAL 1 DAY,
    d2 WITH FILL;

SELECT a, b FROM t ORDER BY a WITH FILL INTERPOLATE (b AS b + 1);

SELECT a, b, c FROM t
ORDER BY a WITH FILL FROM 1 TO 10 STEP 2 INTERPOLATE (b AS b + 1, c);

SELECT a, b FROM t ORDER BY a WITH FILL INTERPOLATE;

-- INTERPOLATE applies to the whole ORDER BY list, so it may trail a later
-- column that itself has no WITH FILL.
SELECT ts, id, value FROM t
ORDER BY ts WITH FILL, id INTERPOLATE (value);
