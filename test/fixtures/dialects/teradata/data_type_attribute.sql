-- Teradata data type attributes applied to an expression as a
-- parenthesised postfix (like COLLATE), on either side of a comparison.
-- https://github.com/sqlfluff/sqlfluff/issues/5530

SELECT 'TEST' (CASESPECIFIC) AS a;

SELECT 'TEST' (NOT CASESPECIFIC) AS a;

SELECT 'TEST' (CS) AS a;

SELECT 'TEST' (NOT CS) AS a;

SELECT col (UPPERCASE) AS a;

SELECT
    CASE
        WHEN 'TEST' (CASESPECIFIC) = 'test' (CASESPECIFIC)
            THEN 'Not true'
        WHEN 'TEST' (NOT CASESPECIFIC) = 'test' (NOT CASESPECIFIC)
            THEN 'True'
        WHEN 'TEST' (CS) = 'test' (CS)
            THEN 'Not true'
        WHEN 'TEST' (NOT CS) = 'test' (NOT CS)
            THEN 'True'
    END AS x;

SELECT
    CASE
        WHEN some_table.attribute1 = 'test' (CASESPECIFIC)
            THEN 'Not true'
        WHEN some_table.attribute1 = 'Test' (NOT CASESPECIFIC)
            THEN 'True'
    END AS x
FROM some_database.some_table AS some_table;
