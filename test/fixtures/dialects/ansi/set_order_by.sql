-- https://github.com/sqlfluff/sqlfluff/issues/852
SELECT 1 AS a
UNION ALL
SELECT 1 AS a
ORDER BY a
