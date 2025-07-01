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

-- Pattern Matching with symbols
SELECT * ~~ 'col%'
FROM tbl;

SELECT * ~~* 'col%'
FROM tbl;

SELECT * !~~ 'col%'
FROM tbl;

SELECT * ~~~ 'col*'
FROM tbl;

SELECT COLUMNS(['id', 'num']) FROM numbers;

SELECT COALESCE(*COLUMNS([upper(x) for x in ['a', 'b', 'c']])) AS result
FROM (SELECT NULL AS a, 42 AS b, true AS c);
