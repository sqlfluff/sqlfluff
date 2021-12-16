-- https://github.com/sqlfluff/sqlfluff/issues/827

SELECT
  a AND NOT i.b
FROM i
