-- redshift_pattern_match_expressions.sql
/* examples of pattern match expressions
( https://docs.aws.amazon.com/redshift/latest/dg/pattern-matching-conditions.html )
that are supported in redshift. */

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

-- SIMILAR TO expressions supported
SELECT *
FROM animals
WHERE family SIMILAR TO '%ursidae%';

SELECT *
FROM animals
WHERE family NOT SIMILAR TO '%ursidae%';

SELECT *
FROM animals
WHERE genus SIMILAR TO '%ursus%';

SELECT *
FROM animals
WHERE genus NOT SIMILAR TO '%ursus%';

SELECT *
FROM animals
WHERE family SIMILAR TO '%ursidae%' ESCAPE '\\';

SELECT *
FROM animals
WHERE genus NOT SIMILAR TO '%ursus%' ESCAPE '\\';

SELECT COALESCE(family SIMILAR TO '%ursidae%' ESCAPE '\\', FALSE) AS is_bear
FROM animals;

-- From https://github.com/sqlfluff/sqlfluff/issues/2722
WITH cleaned_bear_financial_branch AS (
    SELECT
        branch_id,
        TO_NUMBER(CASE WHEN honey_numerical_code SIMILAR TO '[0-9]{0,7}.?[0-9]{0,2}' THEN honey_numerical_code ELSE NULL END, '24601') AS honey_numerical_code
    FROM bear_financial_branch
)

SELECT branch_id
FROM cleaned_bear_financial_branch
LIMIT 10;
