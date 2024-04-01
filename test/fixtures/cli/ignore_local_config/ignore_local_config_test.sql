-- This query raises AL02.
-- We exclude this rule in the .sqlfluff file and then test
-- ignoring this config file via the --ignore-local-config CLI flag.
SELECT col_a a
FROM foo
