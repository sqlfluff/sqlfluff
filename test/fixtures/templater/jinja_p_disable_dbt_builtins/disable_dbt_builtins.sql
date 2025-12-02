-- To test if dbt builtins have been disabled we try to call
-- `var` as a variable instead of as a function
SELECT {{ var }}
