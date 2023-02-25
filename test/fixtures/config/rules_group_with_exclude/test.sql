
/*
Rules group with exclude rules test

If some monster wants to run the core rules, but at the same
time allow trailing and leading commas, then they can do that now

This query should only trigger CP01
*/

SELECT
    field_1,
    field_2
    , field_3
from bar
