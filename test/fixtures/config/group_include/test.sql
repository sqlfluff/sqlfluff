
/*
Allowlist group test

This query violates L027, L044, L050, and L051.
When we include L050 and L051 in test_group in the config we expect L050
and L051 only to be raised by the linter.
*/

SELECT *
FROM bar
JOIN baz
