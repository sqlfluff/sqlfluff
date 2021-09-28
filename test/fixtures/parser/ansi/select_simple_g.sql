-- Having Clause
SELECT
    id
FROM test
WHERE
    id >= 4
GROUP BY id
HAVING id < 5
