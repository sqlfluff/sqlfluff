-- test parsing of cross join
SELECT
    count_correctly_substituted
FROM
    correctly_substituted
CROSS JOIN
    needs_substitution
