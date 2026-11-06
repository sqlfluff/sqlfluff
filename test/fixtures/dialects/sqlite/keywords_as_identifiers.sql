-- MATCH, VIRTUAL and LAST are keywords that SQLite also accepts as identifiers
-- (they are in the %fallback list of the SQLite grammar).
SELECT l.name
FROM Match AS m
INNER JOIN League AS l ON m.league_id = l.id
WHERE m.season = '2008/2009';

SELECT COUNT(*) FROM schools WHERE schools.Virtual = 'F';

SELECT last.milliseconds FROM results AS last;

-- The keyword uses still parse
SELECT a FROM t WHERE x MATCH 'foo';

SELECT a FROM t ORDER BY a NULLS LAST;
