-- SET VARIABLE
SET VARIABLE my_var = 30;
SET VARIABLE other_var TO 'hello';

-- Basic SET parameter = value
SET memory_limit = '10GB';
SET threads = 1;

-- SET parameter TO value
SET threads TO 1;

-- SET SESSION parameter = value
SET SESSION default_collation = 'nocase';

-- SET GLOBAL parameter = value
SET GLOBAL sort_order = 'desc';
SET GLOBAL threads = 4;


-- SET LOCAL parameter = value
SET LOCAL sort_order = 'desc';

-- SET VARIABLE accepts expressions and scalar subqueries.
SET VARIABLE total = 1 + 2;
SET VARIABLE greeting TO upper('hello');
SET VARIABLE answer = (SELECT 42);
SET VARIABLE files = (
    SELECT list(file)
    FROM (VALUES ('a.csv'), ('b.csv')) AS input_files(file)
);

-- Existing literal assignments remain supported.
SET VARIABLE filenames = ['a.csv', 'b.csv'];
SET VARIABLE start_date = DATE '2026-01-01';
