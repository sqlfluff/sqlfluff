-- https://www.postgresql.org/docs/current/sql-createtype.html
CREATE TYPE foo;
CREATE TYPE bar AS ENUM ();
CREATE TYPE bar AS ENUM ('foo', 'bar');
CREATE TYPE foobar AS RANGE (SUBTYPE = FLOAT);
CREATE TYPE barbar AS (INPUT = foo, OUTPUT = bar);
CREATE TYPE foofoo AS (foo varchar collate utf8);
