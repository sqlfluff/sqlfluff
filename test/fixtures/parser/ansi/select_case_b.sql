SELECT
    CASE some_var
    WHEN 'hello' THEN 3
    WHEN 'hi' THEN 12
    ELSE 0
    END as a_case_statement
FROM boo
