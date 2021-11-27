
/*
Denylist glob test

This query violates L027, L044, L050, L051, and L052.
When we exclude L05*,L027 in the config we expect L027, L050, L051,
and L052 to be ignored by the linter.
*/

SELECT *
FROM bar
JOIN baz
