-- PostgreSQL allows an explicit sort operator via `USING operator`
-- instead of ASC/DESC.
-- https://www.postgresql.org/docs/current/queries-order.html
SELECT * FROM t ORDER BY a USING <;

SELECT * FROM t ORDER BY a USING >;

SELECT * FROM t ORDER BY a USING < NULLS FIRST, b USING > NULLS LAST;

SELECT * FROM t ORDER BY a USING OPERATOR(pg_catalog.<);
