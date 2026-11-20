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

-- The rest of the %fallback keywords are also valid identifiers
CREATE TABLE release (
    savepoint INT,
    begin INT,
    end INT,
    rollback INT,
    deferred INT,
    immediate INT,
    exclusive INT,
    abort INT,
    fail INT,
    ignore INT,
    replace INT
);

CREATE TABLE trigger (
    before INT,
    after INT,
    instead INT,
    of INT,
    each INT,
    row INT,
    for INT,
    temp INT,
    view INT,
    with INT,
    without INT,
    recursive INT
);

CREATE TABLE pragma (
    analyze INT,
    attach INT,
    detach INT,
    database INT,
    vacuum INT,
    reindex INT,
    rename INT,
    explain INT,
    query INT,
    plan INT,
    column INT,
    conflict INT,
    do INT
);

CREATE TABLE partition (
    current INT,
    following INT,
    preceding INT,
    unbounded INT,
    range INT,
    rows INT,
    groups INT,
    exclude INT,
    others INT,
    nulls INT,
    first INT,
    offset INT
);

CREATE TABLE cascade (
    restrict INT,
    no INT,
    initially INT,
    generated INT,
    always INT,
    materialized INT,
    asc INT,
    desc INT,
    by INT,
    like INT,
    glob INT,
    regexp INT,
    current_date TEXT,
    current_time TEXT,
    current_timestamp TEXT
);

SELECT savepoint, begin, end FROM release AS rollback;

SELECT before, after, of FROM trigger AS each WHERE row > 0;

SELECT r.asc, r.desc, r.by FROM cascade AS r ORDER BY r.desc DESC;

SELECT first, offset FROM partition LIMIT 1 OFFSET 1;

CREATE TABLE temporary (temporary INT);

SELECT upper(ignore), coalesce(abort, 'x'), max(fail, rollback) FROM release;
