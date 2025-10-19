-- Test 1: Basic BULK COLLECT INTO with single column
SELECT foobar_table.foo
BULK COLLECT INTO selected_foo_bars
FROM foobar_table
WHERE foobar_table.id = foobar_table.foo_bar_id;

-- Test 2: BULK COLLECT INTO with multiple columns
SELECT
    foobar_table.foo,
    foobar_table.bar
BULK COLLECT INTO selected_foo_bars, selected_bar_bars
FROM foobar_table
WHERE foobar_table.id = foobar_table.foo_bar_id;

-- Test 3: BULK COLLECT INTO with expressions and functions
SELECT
    foobar_table.foo * 2,
    UPPER(foobar_table.bar),
    LENGTH(foobar_table.foo)
BULK COLLECT INTO selected_foo_bars, selected_bar_bars, selected_lengths
FROM foobar_table
WHERE foobar_table.id = foobar_table.foo_bar_id;

-- Test 4: BULK COLLECT INTO with subquery and CASE expression
SELECT
    (
        SELECT MAX(id) FROM other_table
        WHERE other_table.ref_id = foobar_table.id
    ),
    CASE
        WHEN foobar_table.foo = 'A' THEN 'Alpha'
        WHEN foobar_table.foo = 'B' THEN 'Beta'
        ELSE 'Other'
    END
BULK COLLECT INTO selected_max_ids, selected_categories
FROM foobar_table
WHERE foobar_table.id = foobar_table.foo_bar_id;

-- Test 5: BULK COLLECT INTO with DISTINCT and ORDER BY
SELECT DISTINCT foobar_table.foo
BULK COLLECT INTO selected_unique_foos
FROM foobar_table
WHERE foobar_table.id = foobar_table.foo_bar_id
ORDER BY foobar_table.foo;

-- Test 6: BULK COLLECT INTO with window functions and aggregates
SELECT
    foobar_table.foo,
    ROW_NUMBER() OVER (ORDER BY foobar_table.foo) AS row_num,
    AVG(foobar_table.value) OVER (PARTITION BY foobar_table.category)
BULK COLLECT INTO selected_foo_bars, selected_row_nums, selected_avgs
FROM foobar_table
WHERE foobar_table.id = foobar_table.foo_bar_id;

-- Test 7: BULK COLLECT INTO with date and string functions
SELECT
    foobar_table.foo,
    SYSDATE,
    CONCAT(foobar_table.foo, '_suffix'),
    SUBSTR(foobar_table.foo, 1, 3)
BULK COLLECT INTO
    selected_foos,
    selected_sysdates,
    selected_concat,
    selected_substr
FROM foobar_table
WHERE foobar_table.id = foobar_table.foo_bar_id;

-- Test 8: BULK COLLECT INTO with conditional logic and complex expressions
SELECT
    foobar_table.foo,
    CASE
        WHEN foobar_table.value > 100 THEN 'High'
        WHEN foobar_table.value > 50 THEN 'Medium'
        ELSE 'Low'
    END AS value_category,
    foobar_table.value * 1.1
BULK COLLECT INTO selected_foos, selected_categories, selected_values
FROM foobar_table
WHERE foobar_table.id = foobar_table.foo_bar_id;
