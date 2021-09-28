-- test some more advanced constructs
SELECT
    a, b
FROM boo
GROUP BY 1
ORDER BY b, 1
LIMIT 5
