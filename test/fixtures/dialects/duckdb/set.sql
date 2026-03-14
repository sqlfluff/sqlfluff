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
