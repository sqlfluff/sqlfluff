-- `left` and `right` are only reserved as unquoted table aliases, so they
-- are usable as lambda parameters and as ordinary column identifiers.

-- The documented `array_sort` example from the Databricks function reference.
SELECT array_sort(ARRAY(3, 1), (left, right) -> CASE WHEN left < right THEN -1 ELSE 1 END);

-- A single bare lambda parameter.
SELECT transform(my_arr, left -> left + 1);

-- `left` and `right` as ordinary column identifiers.
SELECT left, right FROM my_table;
