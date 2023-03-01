
/*
Denylist glob test

This query violates L027, AM04 (ex L044), L050, AM05 (ex L051), and L052.
When we exclude L05*,L027 in the config we expect L027, L050, AM05,
and L052 to be ignored by the linter (AM05 because of it's alias).
*/

SELECT *
FROM bar
JOIN baz
