-- test parsing of cross join and outer join
SELECT
    count_correctly_substituted
FROM
    correctly_substituted
CROSS JOIN
    needs_substitution
LEFT OUTER JOIN
    some_other_table
