-- test window functions in functions with casting
SELECT
    DATEADD(DAY, ROW_NUMBER() OVER (ORDER BY DateCD ASC), '2014-01-01') AS dt
FROM boo
