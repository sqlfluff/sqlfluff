-- postgres_pattern_match_expressions.sql
/* examples of pattern match expressions
( https://www.postgresql.org/docs/14/functions-matching.html ) that are
supported in postgres. */

-- LIKE/ILIKE expressions supported
SELECT *
FROM animals
WHERE family LIKE '%ursidae%';

SELECT *
FROM animals
WHERE family NOT LIKE '%ursidae%';

SELECT *
FROM animals
WHERE genus ILIKE '%ursus%';

SELECT *
FROM animals
WHERE genus NOT ILIKE '%ursus%';

SELECT *
FROM animals
WHERE family LIKE '%ursidae%' ESCAPE '\\';

SELECT *
FROM animals
WHERE genus NOT ILIKE '%ursus%' ESCAPE '\\';

SELECT COALESCE(family LIKE '%ursidae%' ESCAPE '\\', FALSE) AS is_bear
FROM animals;
