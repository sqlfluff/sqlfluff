-- https://www.postgresql.org/docs/current/sql-altertype.html
ALTER TYPE foo RENAME TO bar;
ALTER TYPE foo OWNER TO CURRENT_USER;
ALTER TYPE foo OWNER TO new_owner;
ALTER TYPE foo SET SCHEMA new_schema;
ALTER TYPE compfoo ADD ATTRIBUTE f3 int, DROP ATTRIBUTE IF EXISTS f4, ALTER ATTRIBUTE f5 TYPE int;
ALTER TYPE compfoo RENAME ATTRIBUTE f6 TO f7;
ALTER TYPE colors ADD VALUE 'orange' AFTER 'red';
ALTER TYPE foo ADD VALUE 'baz';
ALTER TYPE foo ADD VALUE 'qux' BEFORE 'baz';
ALTER TYPE foo ADD VALUE 'quux' AFTER 'baz';
ALTER TYPE financial.reporting_statuses RENAME VALUE 'partially' TO 'partially-reported';
