-- https://github.com/sqlfluff/sqlfluff/issues/852
-- ORDER BY and LIMIT are allowed when bracketed. Otherwise not.
(SELECT * FROM a ORDER BY 1 LIMIT 1)
UNION ALL
(SELECT * FROM b ORDER BY 1 LIMIT 1)
ORDER BY 1 LIMIT 1
