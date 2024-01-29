SELECT * EXCLUDE y REPLACE (3 AS x)
FROM tabx;

-- The x column is replaced, but z is not
SELECT * EXCLUDE y REPLACE 3 AS x, 6 as z
FROM tabx;
