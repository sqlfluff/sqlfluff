-- https://github.com/sqlfluff/sqlfluff/issues/828
-- https://github.com/sqlfluff/sqlfluff/issues/842
-- https://www.postgresql.org/docs/9.0/functions-matching.html#FUNCTIONS-LIKE
SELECT *
FROM my_tbl
WHERE a !~ '[a-z]'
AND d !~~* '[a-z]'
AND b LIKE 'Spec\'s%'
AND c !~* '^([0-9]){1,}(\.)([0-9]{1,})$'
