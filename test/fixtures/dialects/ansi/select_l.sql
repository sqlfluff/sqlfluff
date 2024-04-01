-- Nested scalar query
-- https://github.com/sqlfluff/sqlfluff/issues/147
SELECT
  a
FROM
  dat
WHERE
  c >= (SELECT 1)
