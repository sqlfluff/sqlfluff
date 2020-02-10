-- Like and Not Like
-- https://github.com/alanmcruickshank/sqlfluff/issues/170
SELECT *
FROM test
WHERE name NOT LIKE '%y';