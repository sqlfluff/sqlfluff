-- The type name of a column is optional in SQLite.
-- https://www.sqlite.org/syntax/column-def.html
CREATE TABLE a (x);

CREATE TABLE a (x, y);

CREATE TABLE a (x, y INTEGER, z TEXT NOT NULL);

CREATE TABLE a (x NOT NULL, y UNIQUE, z PRIMARY KEY, w DEFAULT 1);

CREATE TABLE a (
    x COLLATE NOCASE,
    y REFERENCES t (a),
    z AS (x + 1),
    v GENERATED ALWAYS AS (x * 2) STORED
);

CREATE TABLE a (x CONSTRAINT nn NOT NULL, y CHECK (y > 0));

ALTER TABLE t ADD COLUMN zz;

ALTER TABLE t ADD zz NOT NULL DEFAULT 0;
