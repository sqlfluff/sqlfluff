-- PRIMARY KEY and UNIQUE table constraints take indexed columns, which can
-- have a COLLATE, ASC or DESC.
-- https://www.sqlite.org/syntax/table-constraint.html
CREATE TABLE a (x INTEGER, y INTEGER, PRIMARY KEY (x ASC));

CREATE TABLE a (x INTEGER, y INTEGER, PRIMARY KEY (x, y DESC));

CREATE TABLE a (x TEXT, y TEXT, UNIQUE (x COLLATE NOCASE, y));

CREATE TABLE a (x INTEGER, UNIQUE (x DESC) ON CONFLICT IGNORE);

CREATE TABLE a (
    x TEXT,
    CONSTRAINT pk PRIMARY KEY (x COLLATE NOCASE DESC) ON CONFLICT REPLACE
);

CREATE TABLE a (x INTEGER, y INTEGER, PRIMARY KEY (x, y), UNIQUE (y, x));
