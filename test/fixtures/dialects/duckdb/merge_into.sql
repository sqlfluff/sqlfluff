-- https://duckdb.org/docs/stable/sql/statements/merge_into
MERGE INTO people
    USING (
        SELECT
            unnest([3, 1]) AS id,
            unnest(['Sarah', 'John']) AS name,
            unnest([95_000.0, 105_000.0]) AS salary
    ) AS upserts
    ON (upserts.id = people.id)
    WHEN MATCHED THEN UPDATE
    WHEN NOT MATCHED THEN INSERT;

MERGE INTO people
    USING (
        SELECT
            1 AS id,
            98_000.0 AS salary
    ) AS salary_updates
    USING (id)
    WHEN MATCHED THEN UPDATE SET salary = salary_updates.salary;

MERGE INTO people
    USING (
        SELECT
            unnest([3, 2]) AS id,
    ) AS deletes
    USING (id)
    WHEN MATCHED AND people.salary >= 100_000.0 THEN DELETE;

MERGE INTO people
    USING (
        SELECT
            unnest([3, 1]) AS id,
            unnest([89_000.0, 70_000.0]) AS salary
    ) AS upserts
    USING (id)
    WHEN MATCHED AND people.salary < 100_000.0 THEN UPDATE SET salary = upserts.salary
    WHEN MATCHED AND people.salary > 100_000.0 THEN DELETE
    WHEN NOT MATCHED THEN INSERT BY NAME
    RETURNING merge_action, id, salary;

-- More than one column, and a plain table as the source.
MERGE INTO people USING new_people USING (id, name)
WHEN NOT MATCHED THEN INSERT;

MERGE INTO people AS p USING new_people AS n ON p.id = n.id
WHEN MATCHED THEN UPDATE
WHEN NOT MATCHED BY SOURCE THEN UPDATE SET salary = 0
WHEN NOT MATCHED BY TARGET THEN INSERT BY NAME;

MERGE INTO people
USING (SELECT 4 AS id, 'Mia' AS name, 80_000.0 AS salary) AS src
USING (id)
WHEN NOT MATCHED THEN INSERT VALUES (src.id, src.name, src.salary);
