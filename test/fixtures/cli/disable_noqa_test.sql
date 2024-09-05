-- Test to verify that --disable-noqa CLI option
-- allows for inline noqa comments to be ignored.
-- NOTE: two noqas so that we can also test --warn-unused-ignores
SELECT
    col_a AS a,  --noqa: CP01
    col_b as b,  --noqa: CP01
    UPPER(col_b) as c, --noqa: CP01
    lower(col_b) as d,  --noqa: CP01, CP03
    lower(col_b) as e  --noqa: core
FROM t;
