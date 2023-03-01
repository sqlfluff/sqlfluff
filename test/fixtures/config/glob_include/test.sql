
/*
Allowlist glob test

This query violates RF02, L044, L050, L051, and L052.
When we include L05*,RF02 in the config we expect RF02, L050, L051,
and L052 only to be raised by the linter.
*/

SELECT *
FROM bar
JOIN baz
