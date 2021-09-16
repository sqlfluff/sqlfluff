-- https://github.com/sqlfluff/sqlfluff/issues/871
WITH constants AS (
    SELECT 8760 AS hours_per_year
)

SELECT
    table1.name,
    foo.name,
    foo.value * constants.hours_per_year AS some_value
FROM table1
CROSS JOIN
    constants
JOIN table2 AS foo USING (id)
