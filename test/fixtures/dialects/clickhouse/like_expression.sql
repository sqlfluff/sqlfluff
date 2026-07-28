-- REGEXP
SELECT 'string' REGEXP '[a-zAZ]';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' REGEXP '[0-9]') AS String) REGEXP '[0123]' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database REGEXP '^sys.*$';


-- LIKE
SELECT 'string' LIKE 's%';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' LIKE 's%') AS String) LIKE '%0%' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database LIKE 'sys%';


-- NOT LIKE
SELECT 'string' NOT LIKE 's%';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' LIKE 's%') AS String) NOT LIKE '%0%' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database NOT LIKE 'sys%';


-- ILIKE
SELECT 'string' ILIKE 'S%';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' ILIKE 'S%') AS String) LIKE '%0%' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database ILIKE 'sYs%';


-- NOT ILIKE
SELECT 'string' NOT ILIKE 'S%';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' NOT ILIKE 'S%') AS String) LIKE '%0%' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database NOT ILIKE 'sYs%';


-- LIKE ESCAPE
SELECT 'test%value' LIKE 'test|%%' ESCAPE '|';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' LIKE 's%' ESCAPE '|') AS String) LIKE '%0%' ESCAPE '|' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database LIKE 'sy%' ESCAPE '|';


-- NOT LIKE ESCAPE
SELECT 'test%value' NOT LIKE 'est|%%' ESCAPE '|';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' LIKE 's%' ESCAPE '|') AS String) NOT LIKE '%0%' ESCAPE '|' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database NOT LIKE 'sy%' ESCAPE '|';


-- ILIKE ESCAPE
SELECT 'test%value' ILIKE 'Test|%%' ESCAPE '|';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' ILIKE 'S%' ESCAPE '|') AS String) LIKE '%0%' ESCAPE '|' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database LIKE 'sY%' ESCAPE '|';


-- NOT ILIKE ESCAPE
SELECT 'test%value' NOT ILIKE 'Est|%%' ESCAPE '|';

SELECT
CASE
    WHEN field = 0 THEN 'false'
    ELSE 'true'
END
FROM (
   SELECT CAST(('string' NOT ILIKE 'S%' ESCAPE '|') AS String) LIKE '%0%' ESCAPE '|' AS field
) AS foo;

SELECT name
FROM system.columns
WHERE database NOT ILIKE 'sY%' ESCAPE '|';
