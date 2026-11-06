-- SET ACCESS METHOD was added in PostgreSQL 15, and accepting DEFAULT in
-- PostgreSQL 17.
-- https://www.postgresql.org/docs/current/sql-altertable.html

ALTER TABLE my_table SET ACCESS METHOD heap;
ALTER TABLE my_table SET ACCESS METHOD DEFAULT;
ALTER TABLE IF EXISTS ONLY my_schema.my_table SET ACCESS METHOD my_access_method;

-- https://www.postgresql.org/docs/current/sql-altermaterializedview.html
ALTER MATERIALIZED VIEW my_view SET ACCESS METHOD heap;
ALTER MATERIALIZED VIEW IF EXISTS my_view SET ACCESS METHOD DEFAULT;
