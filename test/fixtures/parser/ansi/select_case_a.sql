SELECT
    CASE WHEN 1 = 2 THEN 3
    WHEN 4 > 3 THEN 5 + 2
    WHEN some_var IN (1,2,3) then "nothing"
    ELSE "boo"
    END as a_case_statement
FROM boo
