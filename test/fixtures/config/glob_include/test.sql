
/*
Allowlist glob test

This query violates RF02, AM04, L050, AM05, and L052.
When we include L05*,RF02 in the config we expect RF02, L050, AM05,
and L052 only to be raised by the linter (AM05 because it's alias is L051).
*/

SELECT *
FROM bar
JOIN baz
