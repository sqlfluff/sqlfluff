
/*
Denylist glob test

This query violates L027, AB04, L050, AB05, and L052.
When we exclude L05*,L027 in the config we expect L027, L050, AB05,
and L052 to be ignored by the linter.
*/

SELECT *
FROM bar
JOIN baz
