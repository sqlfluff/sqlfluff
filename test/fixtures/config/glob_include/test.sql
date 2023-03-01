
/*
Allowlist glob test

This query violates L027, AM04, L050, AM05, and L052.
When we include L05*,L027 in the config we expect L027, L050, AM05,
and L052 only to be raised by the linter.
*/

SELECT *
FROM bar
JOIN baz
