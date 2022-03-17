{% set x = "col" %}
-- We find the error with the subquery and then have to dump it again
-- due to the template
SELECT *
FROM A_TABLE
INNER JOIN (
    SELECT *, {{ x }}
    FROM B_TABLE
) USING (SOME_COLUMN)
