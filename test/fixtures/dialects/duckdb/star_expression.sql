-- * RENAME
SELECT * RENAME (a AS b)
FROM tbl;

-- Pattern Matching
SELECT * LIKE 'col%'
FROM tbl;

SELECT * ILIKE 'col%'
FROM tbl;

SELECT * NOT LIKE 'col%'
FROM tbl;

SELECT * GLOB 'col*'
FROM tbl;

SELECT * SIMILAR TO 'col.'
FROM tbl;
