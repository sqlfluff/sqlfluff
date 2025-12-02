CREATE TABLE IF NOT EXISTS task (
    id TEXT PRIMARY KEY CHECK (length(id) = 15),
    priority TEXT CHECK (priority GLOB '[A-Z]'),
    regex_col TEXT CHECK (priority REGEXP '[A-Z]'),
    match_col TEXT CHECK (priority MATCH 'tacos'),
    title TEXT NOT NULL,
    note TEXT,
    created_at DATETIME NOT NULL DEFAULT current_timestamp,
    updated_at DATETIME NOT NULL DEFAULT current_timestamp
);

SELECT col1
FROM tab_a
WHERE this_col MATCH 'that';

SELECT col1
FROM tab_a
WHERE this_col REGEXP '(that|other)';

SELECT col1
FROM tab_a
WHERE this_col GLOB 'one*two';

SELECT col1
FROM tab_a
WHERE this_col NOT MATCH 'that';

SELECT col1
FROM tab_a
WHERE this_col NOT REGEXP '(that|other)';

SELECT col1
FROM tab_a
WHERE this_col NOT GLOB 'one*two';

SELECT col1
FROM tab_a
WHERE NOT this_col MATCH 'that';

SELECT col1
FROM tab_a
WHERE NOT this_col REGEXP '(that|other)';

SELECT col1
FROM tab_a
WHERE NOT this_col GLOB 'one*two';
