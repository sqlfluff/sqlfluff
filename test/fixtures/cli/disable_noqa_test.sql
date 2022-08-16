-- Test to verify that --disable-noqa CLI option
-- allows for inline noqa comments to be ignored.
SELECT
    col_a AS a,
    col_b as b  --noqa: L010
FROM t;
