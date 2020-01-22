-- Nested scalar query
-- https://github.com/alanmcruickshank/sqlfluff/issues/147
SELECT
  a
FROM
  dat
WHERE
  c >= (SELECT 1)