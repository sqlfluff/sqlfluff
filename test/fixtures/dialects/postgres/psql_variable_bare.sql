-- psql client variable interpolation without surrounding brackets,
-- as used directly in an expression (see #6686).
-- https://www.postgresql.org/docs/16/app-psql.html#APP-PSQL-INTERPOLATION
SELECT count(*)
FROM foo
WHERE status = :status;

SELECT count(*)
FROM foo
WHERE status = :'status';

SELECT count(*)
FROM foo
WHERE status = :"status";
