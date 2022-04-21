
/*
Denylist group test

This query violates L027, L044, L050, and L051.
When we exclude L051 and L052 in test_group in the config we expect L027
and L044 only to be raised by the linter.
*/

SELECT *
FROM bar
JOIN baz
