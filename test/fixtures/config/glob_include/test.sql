
/*
Whitelist glob test

This query violates L044, L050, L051, L052, and L053.
When we include L05* in the config we expect L050, L051,
and L052 only to be raised by the linter.
*/

SELECT *
FROM bar
JOIN baz
