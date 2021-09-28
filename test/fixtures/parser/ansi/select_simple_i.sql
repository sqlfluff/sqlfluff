-- test aliasing
SELECT
    raw_column,
    raw_sch.raw_col,
    simple_explicit as aliased_column_1,
    simple_implicit aliased_column_2,
    an_unaliased + calculation,
    -- We know that the following one doesn't parse...
    -- an_implicitly + aliased calculation,
    an_explicitly - aliased as calculation,
    'an unalised string',
    123.6,
    -786 as aliased_column3
FROM unaliased
JOIN aliased_1 as foo
JOIN aliased_2 bar USING(b)
