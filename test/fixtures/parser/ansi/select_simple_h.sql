-- test window functions in functions with casting
SELECT
    dateadd('day', row_number() OVER (ORDER BY seq8() asc), '2014-01-01')::date AS dt
FROM boo
