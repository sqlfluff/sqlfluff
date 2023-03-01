
/*
Denylist glob test

This query violates RF02, L044, L050, L051, and L052.
When we exclude L05*,RF02 in the config we expect RF02, L050, L051,
and L052 to be ignored by the linter.
*/

SELECT *
FROM bar
JOIN baz
